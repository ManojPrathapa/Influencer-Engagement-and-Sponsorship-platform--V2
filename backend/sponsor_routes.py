# sponsor.py
# Controller for sponsor login and registration....

from flask import Blueprint, request, jsonify, Response
from models import db, User, Sponsor, Campaign, AdRequest, Influencer, UserFlag, CampaignFlag, Negotiation
from functools import wraps
from flask_cors import cross_origin
import jwt
from datetime import datetime, timedelta
import csv
from io import StringIO

from config import cache

sponsor = Blueprint("sponsor_bp", __name__)
SECRET_KEY = 'your_secret_key'


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            token = token.split(" ")[1]  # Get token from "Bearer <token>"
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        return f(*args, **kwargs)
    return decorated_function


def sponsor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.user.get('role') != 'sponsor':
            return jsonify({"message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


@sponsor.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        sponsor_data = Sponsor.query.filter_by(user_id=user.user_id).first()
        
        if sponsor_data and not sponsor_data.is_approved:
            return jsonify({"message": "Sponsor account is not approved yet"}), 403
        
        token = jwt.encode({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')
        user.login_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"token": token, "role": user.role}), 200
    return jsonify({"message": "Invalid credentials"}), 401


@sponsor.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    company_name = data.get("company_name")
    industry = data.get("industry")
    budget = data.get("budget")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(username=username, email=email, role="sponsor")
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        new_sponsor = Sponsor(
            user_id=new_user.user_id,
            company_name=company_name,
            industry=industry,
            budget=budget,
        )
        db.session.add(new_sponsor)
        db.session.commit()
        return jsonify({"message": "New Sponsor registered successfully"}), 201

    except Exception as e:
        error_message = str(e).split("\n")[0]
        db.session.rollback()
        return jsonify({"message": error_message}), 400


@sponsor.route("/dashboard/data", methods=["GET"])
@cross_origin()
@token_required
@sponsor_required
@cache.cached(timeout=60, key_prefix='sponsor_dashboard_data')
def dashboard_data():
    try:
        user_id = request.user.get('user_id')
        sponsor = Sponsor.query.filter_by(user_id=user_id).first()

        if not sponsor:
            return jsonify({"message": "Sponsor not found"}), 404

        campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
        campaign_data = [campaign.to_dict() for campaign in campaigns]
        return jsonify({"campaigns": campaign_data}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@sponsor.route("/addcampaign", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def add_campaign():
    data = request.json
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        new_campaign = Campaign(
            sponsor_id=sponsor_data.sponsor_id,
            name=data.get("name"),
            description=data.get("description"),
            start_date=datetime.strptime(data.get("startDate"), "%Y-%m-%d").date(),
            end_date=datetime.strptime(data.get("endDate"), "%Y-%m-%d").date(),
            budget=data.get("budget"),
            visibility=data.get("visibility"),
            goals=data.get("goals"),
            niche=data.get("niche"),
        )

        db.session.add(new_campaign)
        db.session.commit()
        cache.delete('sponsor_dashboard_data')
        return jsonify({"message": "New campaign added successfully", "success": True}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500


@sponsor.route("/campaign/<int:campaign_id>", methods=["GET"])
@cross_origin()
@token_required
@sponsor_required
def get_campaign(campaign_id):
    try:
        campaign = Campaign.query.get(campaign_id)

        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404

        campaign_data = campaign.to_dict()
        return jsonify({"campaign": campaign_data}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@sponsor.route("/editcampaign/<int:campaign_id>", methods=["PUT"])
@cross_origin()
@token_required
@sponsor_required
def edit_campaign(campaign_id):
    data = request.json
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404

        campaign.name = data.get("name")
        campaign.description = data.get("description")
        campaign.start_date = datetime.strptime(data.get("startDate"), "%Y-%m-%d").date()
        campaign.end_date = datetime.strptime(data.get("endDate"), "%Y-%m-%d").date()
        campaign.budget = data.get("budget")
        campaign.visibility = data.get("visibility")
        campaign.goals = data.get("goals")
        campaign.niche = data.get("niche")

        db.session.commit()

        return jsonify({"message": "Campaign updated successfully", "success": True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500


@sponsor.route("/export_campaigns", methods=["GET"])
@cross_origin()
@token_required
@sponsor_required
def export_campaigns():
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_data.sponsor_id).all()

        def generate():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(["Name", "Description", "Niche", "Budget", "Start Date", "End Date", "Goals", "Visibility"])
            for campaign in campaigns:
                writer.writerow([
                    campaign.name,
                    campaign.description,
                    campaign.niche,
                    str(campaign.budget),
                    campaign.start_date.strftime("%Y-%m-%d"),
                    campaign.end_date.strftime("%Y-%m-%d"),
                    campaign.goals,
                    campaign.visibility
                ])
            yield data.getvalue()
            data.seek(0)

        return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=campaigns.csv"})

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@sponsor.route("/deletecampaign/<int:campaign_id>", methods=["DELETE"])
@cross_origin()
@token_required
@sponsor_required
def delete_campaign(campaign_id):
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404

        db.session.delete(campaign)
        db.session.commit()
        cache.delete(f'sponsor_campaign_data_{campaign_id}')
        cache.delete('sponsor_dashboard_data')
        return jsonify({"message": "Campaign deleted successfully", "success": True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500


@sponsor.route("/adrequest_data/<int:campaign_id>", methods=["GET","POST"])
@cross_origin()
@token_required
@sponsor_required
# # @cache.cached(timeout=60, key_prefix='sponsor_adrequest_data')
def adrequest_campaign(campaign_id):
    try:
        adrequests = (
            db.session.query(AdRequest, Influencer, Campaign, Sponsor, Negotiation)
            .join(Influencer, AdRequest.influencer_id == Influencer.influencer_id)
            .join(Campaign, AdRequest.campaign_id == Campaign.campaign_id)
            .join(Sponsor, Campaign.sponsor_id == Sponsor.sponsor_id)
            .outerjoin(Negotiation, AdRequest.ad_request_id == Negotiation.ad_request_id)
            .filter(AdRequest.campaign_id == campaign_id)
            .all()
        )

        adrequest_data = []
        for adrequest, influencer, campaign, sponsor, negotiation in adrequests:
            adrequest_info = adrequest.to_dict()
            adrequest_info['influencer'] = influencer.to_dict()
            adrequest_info['campaign'] = campaign.to_dict()
            adrequest_info['sponsor'] = sponsor.to_dict()
            
            if negotiation:
                adrequest_info['negotiation'] = {
                    'negotiation_id': negotiation.negotiation_id,
                    'negotiation_status': negotiation.negotiation_status,
                    'negotiated_amount': negotiation.proposed_payment_amount
                }
            else:
                adrequest_info['negotiation'] = {
                    'negotiation_id': None,
                    'negotiation_status': None,
                    'negotiated_amount': None
                }

            adrequest_data.append(adrequest_info)
        # print(adrequest_data)
        return jsonify({"adrequests": adrequest_data}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500


@sponsor.route("/add_adRequest_data", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def add_adRequest_data():
    data = request.json
    # print(data)
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404
        payment_amount= data['payment_amount']
        print(type(payment_amount))
        payment_amount= float(data['payment_amount'])
        print(type(payment_amount))

        new_ad_req = AdRequest(
            campaign_id = data['campaign_id'],
            influencer_id=data['influencer_id'],
            requirements=data['requirements'],
            payment_amount= payment_amount,
            messages=data['messages'],
        )
        db.session.add(new_ad_req)
        db.session.commit()


        # Clear cache for ad request data and dashboard data
        cache.delete(f'sponsor_adrequest_data_{data["campaign_id"]}')
        cache.delete('sponsor_dashboard_data')
        return jsonify({"message": "New ad_request added successfully", "success": True}), 201

    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500

@sponsor.route("/edit_adrequest_data/<int:ad_request_id>", methods=["PUT"])
@cross_origin()
@token_required
@sponsor_required
def edit_adRequest_data(ad_request_id):
    data = request.json
    print(data)
    try:
        ad_reqst = AdRequest.query.get(ad_request_id)
        if not ad_reqst:
            return jsonify({"message": "ad_reqst not found"}), 404
        
        ad_reqst.campaign_id = data["campaign_id"]
        ad_reqst.influencer_id= data["influencer_id"]
        ad_reqst.requirements=data["requirements"]
        ad_reqst.payment_amount=data["payment_amount"]
        ad_reqst.status=data["status"]
        ad_reqst.messages=data["messages"]
    
        db.session.commit()

        # Clear cache for ad request data and dashboard data
        cache.delete(f'sponsor_adrequest_data_{ad_reqst.campaign_id}')
        cache.delete('sponsor_dashboard_data')

        return jsonify({"message": "Ad_reqst updated successfully", "success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500
    

@sponsor.route("/approve_adrequest/<int:request_id>", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def approve_ad_request(request_id):
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        # Fetching the ad request based on the request_id
        ad_request = AdRequest.query.get(request_id)
        if not ad_request or ad_request.campaign.sponsor_id != sponsor_data.sponsor_id:
            return jsonify({"message": "Ad request not found or unauthorized"}), 403

        # Approving the ad request
        ad_request.request_status = 'approved'
        db.session.commit()

        return jsonify({"message": "Ad request approved successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@sponsor.route("/reject_adrequest/<int:request_id>", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def reject_ad_request(request_id):
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        # Fetching the ad request based on the request_id
        ad_request = AdRequest.query.get(request_id)
        if not ad_request or ad_request.campaign.sponsor_id != sponsor_data.sponsor_id:
            return jsonify({"message": "Ad request not found or unauthorized"}), 403

        # Rejecting the ad request
        ad_request.request_status = 'rejected'
        db.session.commit()

        return jsonify({"message": "Ad request rejected successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@sponsor.route("/delete_adrequest_data/<int:ad_request_id>", methods=["DELETE"])
@cross_origin()
@token_required
@sponsor_required
def delete_adRequest_data(ad_request_id):
    try:
        ad_reqst = AdRequest.query.get(ad_request_id)
        if not ad_reqst:
            return jsonify({"message": "Ad request not found"}), 404
        
        db.session.delete(ad_reqst)
        db.session.commit()

        # Clear cache for ad request data and dashboard data
        cache.delete('sponsor_adrequest_data')
        cache.delete('sponsor_dashboard_data')

        return jsonify({"message": "Ad request deleted successfully", "success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e), "success": False}), 500


@sponsor.route("/flag_influencer/<int:influencer_id>", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def flag_influencer(influencer_id):
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        # Checking if the influencer has already been flagged
        existing_flag = UserFlag.query.filter_by(user_id=influencer.user_id, sponsor_id=sponsor_data.sponsor_id).first()
        if existing_flag:
            return jsonify({"message": "Influencer already flagged by this sponsor"}), 400

        # Flagging the influencer
        new_flag = UserFlag(user_id=influencer.user_id, sponsor_id=sponsor_data.sponsor_id)
        db.session.add(new_flag)
        db.session.commit()

        return jsonify({"message": "Influencer flagged successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@sponsor.route("/flag_campaign/<int:campaign_id>", methods=["POST"])
@cross_origin()
@token_required
@sponsor_required
def flag_campaign(campaign_id):
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        campaign = Campaign.query.get(campaign_id)
        if not campaign or campaign.sponsor_id != sponsor_data.sponsor_id:
            return jsonify({"message": "Campaign not found or unauthorized"}), 403

        # Checking if the campaign has already been flagged
        existing_flag = CampaignFlag.query.filter_by(campaign_id=campaign_id, sponsor_id=sponsor_data.sponsor_id).first()
        if existing_flag:
            return jsonify({"message": "Campaign already flagged by this sponsor"}), 400

        # Flagging the campaign
        new_flag = CampaignFlag(campaign_id=campaign_id, sponsor_id=sponsor_data.sponsor_id)
        db.session.add(new_flag)
        db.session.commit()

        return jsonify({"message": "Campaign flagged successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@sponsor.route("/view_negotiations", methods=["GET"])
@cross_origin()
@token_required
@sponsor_required
def view_negotiations():
    try:
        user_id = request.user.get('user_id')
        sponsor_data = Sponsor.query.filter_by(user_id=user_id).first()
        if not sponsor_data:
            return jsonify({"message": "Sponsor not found"}), 404

        # Fetching all negotiations associated with the sponsor
        negotiations = Negotiation.query.filter_by(sponsor_id=sponsor_data.sponsor_id).all()
        negotiations_data = [negotiation.to_dict() for negotiation in negotiations]

        return jsonify({"negotiations": negotiations_data}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

