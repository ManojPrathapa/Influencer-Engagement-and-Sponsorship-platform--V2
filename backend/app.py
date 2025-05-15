from flask import Flask, redirect, url_for, flash, make_response, jsonify, request
from models import db, initialize_database, User, Sponsor, Influencer, Campaign, AdRequest
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery
from flask_mail import Mail
from config import cache, AppConfig
from redis import Redis
import random
from flask_cors import cross_origin

# Initialize Flask app instance
application = Flask(__name__)
application.config.from_object(AppConfig)

# Flask-Mail configuration
application.config['MAIL_SERVER'] = 'smtp://localhost:1025'  # Mailhog SMTP server
application.config['MAIL_PORT'] = 1025  # Mailhog default port
application.config['MAIL_USE_TLS'] = False  # No TLS needed for Mailhog
application.config['MAIL_USE_SSL'] = False  # No SSL needed for Mailhog
application.config['MAIL_USERNAME'] = None  # No username required for Mailhog
application.config['MAIL_PASSWORD'] = None  # No password required for Mailhog

application.config['MAIL_DEFAULT_SENDER'] = 'mankojp23@example.com'

# Initialize the Mail instance
mail = Mail(application)

# Import separate route files for modularity
from admin_routes import admin
from sponsor_routes import sponsor
from influencer_routes import influencer

# Celery configuration
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(application)

# Set up database and caching tools
db.init_app(application)  # Integrate SQLAlchemy with Flask
initialize_database(application)  # Custom database initialization
cache.init_app(application)  # Set up caching

# Configure third-party libraries
jwt_manager = JWTManager(application)  # Enable JWT for secure authentication
mail_service = Mail(application)       # Configure email notifications
CORS(application, resources={r"/*": {"origins": "*"}})  # Allow cross-origin requests

# Register route blueprints for better organization
application.register_blueprint(admin, url_prefix="/admin")
application.register_blueprint(sponsor, url_prefix="/sponsor")
application.register_blueprint(influencer, url_prefix="/influencer")

# Set up Redis for caching purposes
redis_connection = Redis(host='localhost', port=6379, db=1)
try:
    redis_connection.ping()
    print("\nRedis is successfully connected!\n")
except Exception as error:
    print(f"\nRedis connection failed: {error}\n")

# Define homepage route
@application.route("/welcome", methods=["GET", "POST"])
def welcome():
    """
    Displays a welcome message with a random number.
    """
    return "Welcome to the platform! " + str(random.randint(100, 999))

# Logout functionality
@application.route("/signout", methods=["POST", "GET"])
def signout():
    """
    Signs the user out by clearing authentication cookies and cache.
    """
    response = make_response(redirect(url_for("welcome")))

    response.set_cookie('auth_token', '', expires=0, path="/")  # Remove the auth cookie

    # Clear Redis cache if active
    if application.config.get('CACHE_TYPE') == 'redis':
        cache_prefix = application.config.get('CACHE_KEY_PREFIX', '')
        for key in redis_connection.scan_iter(f"{cache_prefix}*"):
            redis_connection.delete(key)

    flash("Successfully signed out", "info")
    return response

# API endpoint for retrieving all users
@application.route("/api/all-users", methods=["GET"])
@cache.cached()
@cross_origin()
def get_all_user():
    data = dict()

    data["admin"] = [
        user.to_dict() for user in User.query.filter_by(role="admin").all()
    ]
    data["sponsor"] = [
        user.to_dict() for user in User.query.filter_by(role="sponsor").all()
    ]
    data["influencer"] = [
        user.to_dict() for user in User.query.filter_by(role="influencer").all()
    ]

    return data

# API endpoint for fetching all influencers
@application.route("/api/creators", methods=["GET"])
@cache.cached()
def fetch_influencers():
    """
    Retrieves all influencers from the database.
    """
    try:
        creators = Influencer.query.all()
        return jsonify([creator.to_dict() for creator in creators])
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# Endpoint to fetch a specific influencer by ID
@application.route("/api/creator/<int:creator_id>", methods=["GET"])
@cache.cached()
def fetch_creator_by_id(creator_id):
    """
    Retrieves details of a specific influencer using their unique ID.
    """
    try:
        creator = Influencer.query.get(creator_id)
        if not creator:
            return jsonify({"message": "Creator not found", "success": False}), 404
        return jsonify(creator.to_dict())
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# API for retrieving campaigns
@application.route("/api/campaigns-list", methods=["GET"])
@cache.cached()
@cross_origin()
def list_campaigns():
    """
    Retrieves all campaigns with necessary details.
    """
    try:
        campaigns = Campaign.query.all()
        if not campaigns:
            return jsonify({"message": "No campaigns found", "success": False}), 404
        return jsonify({
            "success": True,
            "campaigns": [campaign.to_dict() for campaign in campaigns]
        })
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# Fetch details of a specific campaign by ID
@application.route("/api/campaign-detail/<int:campaign_id>", methods=["GET"])
@cache.cached()
def campaign_details(campaign_id):
    """
    Retrieves information about a specific campaign by its ID.
    """
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"message": "Campaign not found", "success": False}), 404
        return jsonify(campaign.to_dict())
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# Endpoint for public campaigns
@application.route("/api/available-campaigns", methods=["GET"])
@cache.cached()
def public_campaigns():
    """
    Lists all publicly visible campaigns.
    """
    public_campaigns = db.session.query(Campaign).filter(Campaign.visibility == "public").all()
    return jsonify([campaign.to_dict() for campaign in public_campaigns])

# API for retrieving all ad requests
@application.route("/api/advert-requests", methods=["GET"])
@cache.cached()
def fetch_ad_requests():
    """
    Retrieves all ad requests made in the system.
    """
    try:
        ad_requests = AdRequest.query.all()
        return jsonify([ad_request.to_dict() for ad_request in ad_requests])
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# Fetch specific ad request by ID
@application.route("/api/advert-request/<int:request_id>", methods=["GET"])
@cache.cached(key_prefix='advert_request_data')
def ad_request_by_id(request_id):
    """
    Retrieves the details of a specific ad request by ID.
    """
    try:
        ad_request = AdRequest.query.get(request_id)
        if not ad_request:
            return jsonify({"message": "Ad request not found", "success": False}), 404
        return jsonify(ad_request.to_dict())
    except Exception as ex:
        return jsonify({"error": str(ex), "success": False}), 500

# Run the Flask server
if __name__ == "__main__":
    with application.app_context():
        initialize_database(application)  # Ensure the database is initialized
    application.run(debug=True)

