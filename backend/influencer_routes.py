# influencer.py

from flask import Blueprint, request, jsonify
from models import db, User, Sponsor, Campaign, AdRequest, Influencer, UserFlag, CampaignFlag, Negotiation
from functools import wraps
from flask_cors import cross_origin
import jwt
from datetime import datetime, timedelta
from flask import Response

import helper

from config import cache

influencer = Blueprint("influencer_bp", __name__)
SECRET_KEY = 'your_secret_key'
from flask_cors import cross_origin



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


def influencer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.user.get('role') != 'influencer':
            return jsonify({"message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


@influencer.route("/login",methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username = username).first()
    # print(user)

    if user and user.check_password(password):
        influencer_data = Influencer.query.filter_by(user_id = user.user_id).first()
        
        # print(influencer_data.to_dict())
        
        token = jwt.encode({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')
        user.login_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"token": token ,  "role": user.role}), 200
    return jsonify({"message": "Invalid credentials"}), 401




@influencer.route("/register" , methods=["POST"])
def register():

    data = request.json
    #Register as User
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    role = data.get("role")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username=username, email=email, role="influencer")
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        #Register as Influencer
        user_id = new_user.user_id
        name = data.get("name")
        category = data.get("category")
        niche = data.get("niche")
        reach = data.get("reach")

        new_influ = Influencer(
                user_id=new_user.user_id,
                category=category,
                name=name,
                niche=niche,
                reach=reach,
            )

        db.session.add(new_influ)
        db.session.commit()
        
        return jsonify({"message": "New Influencer registered successfully"}), 201
    
    except Exception as e:
        error_message = str(e).split("\n")[0]
        db.session.rollback()
        return jsonify({"message": error_message}), 400
    



@influencer.route("/dashboard", methods=["GET", "POST"])
@cross_origin()
@token_required
@influencer_required
@cache.cached(key_prefix='influencer_dashboard')
def dashboard():
    try :
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        # print(influencer)
        
        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404
        
        influencer_id = influencer.influencer_id

        data = helper.get_influencer_campaigns(influencer_id)

        # print(data)
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    



@influencer.route("/acceptAdRequest/<int:ad_request_id>", methods=["POST", "GET"])
@cross_origin()
@token_required
@influencer_required
def acceptAdRqst(ad_request_id:int):
    try:
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404
        
        influencer_id = influencer.influencer_id
        ad_request_id = ad_request_id

        data = helper.get_influencer_campaigns(influencer_id)
        show_info = None
        
        for d in data:
            if d["ad_request_id"] == ad_request_id:
                show_info = d
                break
        if not show_info:
            return jsonify({"message": "Ad request not found"}), 404
    # Check if Already Accepted !!
        if (
            show_info["negotiation_status"] == "accepted"
            and show_info["status"] == "accepted"
        ):
            message ="You have Already Accepted the Ad Request !! "
            return jsonify({"message": message }), 500

        # Check if Already Rejected !!
        elif show_info["negotiation_status"] == "rejected":
            message ="You have Already Rejected the Ad Request !! "
            return jsonify({"message": message }), 500
        
        if request.method == "POST":

            if show_info["negotiation_id"]:
                nego = Negotiation.query.filter_by(
                    negotiation_id=show_info["negotiation_id"]
                ).first()
                nego.negotiation_status = "accepted"
                nego.proposed_payment_amount = show_info["payment_amount"]

                try:
                    db.session.commit()

                except Exception as e:
                    error_message = str(e).split("\n")[0]
                    db.session.rollback()
                    return jsonify({"message": str(error_message)}), 500
            else:
                new_nego = Negotiation(
                    ad_request_id=show_info["ad_request_id"],
                    influencer_id=show_info["influencer_id"],
                    negotiation_status="accepted",
                    proposed_payment_amount=show_info["payment_amount"],
                )

                try:
                    db.session.add(new_nego)
                    db.session.commit()
                except Exception as e:
                    error_message = str(e).split("\n")[0]
                    db.session.rollback()
                    return jsonify({"message": str(error_message)}), 500


            # change ad_request status to accepted !
            ad_reqst = AdRequest.query.filter_by(
                ad_request_id=show_info["ad_request_id"]
            ).first_or_404()
            ad_reqst.status = "accepted"
            try:
                db.session.commit()

            except Exception as e:
                error_message = str(e).split("\n")[0]
                db.session.rollback()
                return jsonify({"message": str(error_message)}), 500

            # #Clear the cache for dashboard data
            cache.delete('influencer_dashboard')
            return {"message" : "AD_reqest Accepted Successfully!"}
        else:
            return show_info

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    





@influencer.route("/rejectAdRequest/<int:ad_request_id>", methods=["POST", "GET"])
@cross_origin()
@token_required
@influencer_required
def reject_adrequest(ad_request_id):

    try:
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404
        
        influencer_id = influencer.influencer_id

        data = helper.get_influencer_campaigns(influencer_id)
        show_info = next((d for d in data if d["ad_request_id"] == ad_request_id), None)

       

        if not show_info:
            return jsonify({"message": "Ad request not found"}), 404
        

        # Check if Already Accepted !!
        if (
            show_info["negotiation_status"] == "accepted"
            and show_info["status"] == "accepted"
        ):
            message = "You have Already Accepted the Ad Request !! "
            return jsonify({"message": message }), 500

        # Check if Already Rejected !!
        if (
            show_info["negotiation_status"] == "rejected"
            and show_info["status"] == "rejected"
        ):
            message= "You have Already Rejected the Ad Request !! "
            return jsonify({"message": message }), 500

        if request.method == "POST":
            # Change Ad_request status
            old_ad_request = AdRequest.query.filter_by(ad_request_id=ad_request_id).first_or_404()
            old_ad_request.status = "rejected"

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": str(e).split("\n")[0]}), 500

            # Change Negotiation status to Rejected
            if show_info["negotiation_id"] is not None:
                old_nego = Negotiation.query.filter_by(negotiation_id=show_info["negotiation_id"]).first_or_404()
                old_nego.negotiation_status = "rejected"
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"message": str(e).split("\n")[0]}), 500
            else:
                new_nego = Negotiation(
                    ad_request_id=ad_request_id,
                    influencer_id=influencer_id,
                    negotiation_status="rejected",
                    proposed_payment_amount=show_info["negotiated_amount"],
                )
                try:
                    db.session.add(new_nego)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"message": str(e).split("\n")[0]}), 500
                
            # #Clear the cache for dashboard data
            cache.delete('influencer_dashboard')
            return {"message" : "AD_reqest Rejected Successfully!"}
        else:
            return jsonify(show_info)

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    


@influencer.route("/negoAdRequest/<int:ad_request_id>", methods=["POST", "GET"])
@cross_origin()
@token_required
@influencer_required
def nego_adrequest(ad_request_id):
    try:
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404
        
        influencer_id = influencer.influencer_id

        data = helper.get_influencer_campaigns(influencer_id)
        show_info = next((d for d in data if d["ad_request_id"] == ad_request_id), None)

        if not show_info:
            return jsonify({"message": "Ad request not found"}), 404

        # Check if Already Accepted
        if show_info["negotiation_status"] == "accepted" and show_info["status"] == "accepted":
            return jsonify({"message": "You have already accepted the ad request!"}), 400

        # Check if Already Rejected
        if show_info["negotiation_status"] == "rejected":
            return jsonify({"message": "You have already rejected the ad request!"}), 400
        
        if request.method == "POST":
            new_nego_amount = request.form.get("nego_amount")
            if not new_nego_amount:
                return jsonify({"message":"Empty Response wont accept !"}) , 500

            # Change Ad_request status
            old_ad_request = AdRequest.query.filter_by(ad_request_id=show_info["ad_request_id"]).first_or_404()
            old_ad_request.status = "negotiation"

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"message": str(e).split("\n")[0]}), 500

            # Change Nego_amount and status
            if show_info["negotiation_id"] is not None:
                old_nego = Negotiation.query.filter_by(negotiation_id=show_info["negotiation_id"]).first_or_404()
                old_nego.proposed_payment_amount = new_nego_amount
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"message": str(e).split("\n")[0]}), 500
            else:
                new_nego = Negotiation(
                    ad_request_id=show_info["ad_request_id"],
                    influencer_id=show_info["influencer_id"],
                    negotiation_status="pending",
                    proposed_payment_amount=new_nego_amount,
                )
                try:
                    db.session.add(new_nego)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"message": str(e).split("\n")[0]}), 500

            return jsonify({"message": f"UPDATED THE Negotiation ({new_nego_amount})"})
        else:
            return jsonify(show_info)

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    


@influencer.route("/sendAdReqst/<int:campaign_id>", methods=["POST"])
@cross_origin()
@token_required
@influencer_required
def sendAdReqst(campaign_id):
    try:
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        influencer_id = influencer.influencer_id
        new_ad = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            requirements="Ad Request from Influencer! Edit and Negotiate it",
            payment_amount=0,
            messages="Payment Amount Yet to be decided!",
        )

        db.session.add(new_ad)
        db.session.commit()

        # #Clear relevant cache
        cache.delete('influencer_dashboard')
        
        return jsonify({"message": "New ad request added successfully", "success": True}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    

@influencer.route("/profile", methods=["GET", "POST"])
@cross_origin()
@token_required
@influencer_required
def influProfile():
    try:
        user_id = request.user.get('user_id')
        influencer = Influencer.query.filter_by(user_id=user_id).first()
        # print(influencer)
        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        # Handle GET request
    
        influ_data = influencer.to_dict()
        # print(influ_data)

        # Handle POST request
        if request.method == "POST":
            data = request.json
            # print("this is data" , data)
            # Validate the incoming data
            if not all(key in data for key in ("name", "niche", "reach")):
                return jsonify({"message": "Missing required fields"}), 400

            # Update influencer details
            influencer.name = data.get("name")
            influencer.niche = data.get("niche")
            influencer.reach = data.get("reach")
            influencer.category = data.get("category")


            db.session.commit()

            return jsonify({"message": "Profile updated successfully"})
        
        else:
            return jsonify({"influ_data": influ_data})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    
'''
@influencer.route("/joinedCampaigns", methods=["GET"])
@cross_origin()
@token_required
@influencer_required
def joined_campaigns():
    """
    Fetch all campaigns that the influencer has joined.
    """
    try:
        user_id = request.user.get("user_id")
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        influencer_id = influencer.influencer_id

        joined_campaigns = (
            db.session.query(Campaign)
            .join(CampaignInfluencer, Campaign.campaign_id == CampaignInfluencer.campaign_id)
            .filter(CampaignInfluencer.influencer_id == influencer_id)
            .all()
        )

        campaigns_data = [
            {
                "campaign_id": campaign.campaign_id,
                "title": campaign.title,
                "description": campaign.campaign_description,
                "start_date": campaign.start,
                "end_date": campaign.end,
                "visibility": campaign.visibility,
                "budget": campaign.campaign_budget,
            }
            for campaign in joined_campaigns
        ]

        return jsonify({"campaigns": campaigns_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@influencer.route("/adRequestsSent", methods=["GET"])
@cross_origin()
@token_required
@influencer_required
def ad_requests_sent():
    """
    Fetch all ad requests sent by the influencer.
    """
    try:
        user_id = request.user.get("user_id")
        influencer = Influencer.query.filter_by(user_id=user_id).first()

        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        influencer_id = influencer.influencer_id

        ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()

        ad_requests_data = [
            {
                "ad_request_id": ad_request.request_id,
                "campaign_id": ad_request.campaign_id,
                "content": ad_request.request_content,
                "status": ad_request.request_status,
                "payment_amount": ad_request.payment_amount,
            }
            for ad_request in ad_requests
        ]

        return jsonify({"adRequests": ad_requests_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

'''