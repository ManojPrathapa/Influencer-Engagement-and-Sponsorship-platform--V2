from flask import Blueprint, request, jsonify, current_app
from models import db, User, Sponsor, Campaign, AdRequest, Influencer, UserFlag, CampaignFlag
from functools import wraps
from flask_cors import cross_origin
import jwt
from datetime import datetime, timedelta
from config import cache

# Create Blueprint for admin routes
admin = Blueprint("admin_bp", __name__)

# Secret key for JWT
# SECRET_KEY = current_app.config["SECRET_KEY"]

# Decorators
def token_required(f):
    """
    Decorator to check for a valid JWT token in the Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing!"}), 403
        try:
            token = token.split(" ")[1]  # Extract token from Bearer <Token>
            SECRET_KEY = current_app.config["SECRET_KEY"]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 403
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to restrict access to admin routes only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.user.get('role') != 'admin':
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


# Routes
@admin.route("/login", methods=["POST"])
def login():
    """
    Admin login to obtain a JWT token.
    """
    data = request.get_json()
    if not data or not all(field in data for field in ["username", "password"]):
        return jsonify({"error": "Missing username or password"}), 400

    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    SECRET_KEY = current_app.config["SECRET_KEY"]
    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        user.login_date = datetime.utcnow()
        db.session.commit()

        return jsonify({"token": token, "role": user.role}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@admin.route("/register", methods=["POST"])
def register():
    """
    Register a new admin user.
    """
    data = request.get_json()
    required_fields = ["username", "password", "email", "role"]
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    username = data["username"]
    password = data["password"]
    email = data["email"]
    role = data["role"]

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@admin.route("/dashboard/data", methods=["GET"])
@cross_origin()
@token_required
@admin_required
@cache.cached(key_prefix='dashboard_data')
def dashboard_data():
    try:
        data = {
            "total_users": User.query.count(),
            "total_sponsors": Sponsor.query.count(),
            "total_campaigns_public": Campaign.query.filter_by(visibility="public").count(),
            "total_campaigns_private": Campaign.query.filter_by(visibility="private").count(),
            "total_ad_requests_pending": AdRequest.query.filter_by(status="pending").count(),
            "total_ad_requests_rejected": AdRequest.query.filter_by(status="rejected").count(),
            "total_ad_requests_negotiation": AdRequest.query.filter_by(status="negotiation").count(),
            "total_ad_requests_accepted": AdRequest.query.filter_by(status="accepted").count(),
            "total_influencers": Influencer.query.count(),
            "flagged_users": UserFlag.query.count(),
            "flagged_campaigns": CampaignFlag.query.count(),
            "pending_sponsors": Sponsor.query.filter_by(is_approved=False).count()  # Count pending sponsors
        }
        # print(data)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin.route("/dashboard/graph-data", methods=["GET"])
@cross_origin()
@token_required
@admin_required
def dashboard_graph_data():
    """
    Fetch graph data for admin dashboard.
    """
    try:
        graph_data = {
            "campaign_visibility": {
                "public": Campaign.query.filter_by(visibility="public").count(),
                "private": Campaign.query.filter_by(visibility="private").count()
            },
            "ad_request_statuses": {
                "pending": AdRequest.query.filter_by(status="pending").count(),
                "rejected": AdRequest.query.filter_by(status="rejected").count(),
                "negotiation": AdRequest.query.filter_by(status="negotiation").count(),
                "accepted": AdRequest.query.filter_by(status="accepted").count()
            },
            "user_roles": {
                "admins": User.query.filter_by(role="admin").count(),
                "sponsors": User.query.filter_by(role="sponsor").count(),
                "influencers": User.query.filter_by(role="influencer").count()
            }
        }
        return jsonify({"data": graph_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching graph data: {str(e)}"}), 500


@admin.route("/pending_sponsors", methods=["GET"])
@token_required
@admin_required
@cache.cached()
def pending_sponsors():
    try:
        sponsors = Sponsor.query.filter_by(is_approved=False).all()
        return jsonify([sponsor.to_dict() for sponsor in sponsors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin.route("/approve_sponsor/<int:sponsor_id>", methods=["POST"])
@token_required
@admin_required
def approve_sponsor(sponsor_id):
    try:
        sponsor = Sponsor.query.get(sponsor_id)
        if not sponsor:
            return jsonify({"message": "Sponsor not found"}), 404
        sponsor.is_approved = True
        db.session.commit()

        cache.delete('dashboard_data')
        return jsonify({"message": "Sponsor approved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin.route("/reject_sponsor/<int:sponsor_id>", methods=["POST"])
@token_required
@admin_required
def reject_sponsor(sponsor_id):
    """
    Reject a pending sponsor.
    """
    try:
        sponsor = Sponsor.query.get(sponsor_id)
        if not sponsor:
            return jsonify({"error": "Sponsor not found"}), 404

        db.session.delete(sponsor)
        db.session.commit()

        return jsonify({"message": f"Sponsor {sponsor_id} rejected"}), 200
    except Exception as e:
        return jsonify({"error": f"Error rejecting sponsor: {str(e)}"}), 500


@admin.route("/user_flags", methods=["GET"])
@token_required
@admin_required
def user_flags():
    """
    Get all flagged users.
    """
    try:
        flags = UserFlag.query.all()
        return jsonify([flag.to_dict() for flag in flags]), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching user flags: {str(e)}"}), 500


@admin.route("/campaign_flags", methods=["GET"])
@token_required
@admin_required
def campaign_flags():
    """
    Get all flagged campaigns.
    """
    try:
        flags = CampaignFlag.query.all()
        return jsonify([flag.to_dict() for flag in flags]), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching campaign flags: {str(e)}"}), 500
