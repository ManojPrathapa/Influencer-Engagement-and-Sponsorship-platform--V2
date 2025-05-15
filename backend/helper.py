# helper.py
# Helper functions for database

from models import User, Campaign, Sponsor, AdRequest, Influencer, Negotiation, db
from sqlalchemy import case
from datetime import datetime
import json

# Function to get user data by username
def get_data_by_name(username):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return user.to_dict()  # Assuming to_dict method exists in User model
    else:
        return None

# Function to get campaigns related to an influencer along with ad requests and negotiations
def get_influencer_campaigns(influencer_id):
    # Query to get all the campaigns, ad_requests, negotiations, and sponsor names for the influencer
    campaigns = (
        db.session.query(
            Campaign.campaign_id,
            Campaign.name.label("campaign_name"),
            Campaign.description,
            Campaign.goals,
            Campaign.niche,
            Campaign.sponsor_id,
            Sponsor.company_name.label("sponsor_name"),  # Fetch the sponsor name
            Campaign.start_date,
            Campaign.end_date,
            AdRequest.ad_request_id,
            AdRequest.messages,
            AdRequest.payment_amount,
            AdRequest.requirements,
            AdRequest.status,
            AdRequest.influencer_id,
            Negotiation.negotiation_id,
            case(
                (
                    Negotiation.negotiation_id.isnot(None),
                    Negotiation.proposed_payment_amount,
                ),
                else_=AdRequest.payment_amount,
            ).label("negotiated_amount"),
            case(
                (
                    Negotiation.negotiation_id.isnot(None),
                    Negotiation.negotiation_status,
                ),
                else_=AdRequest.status,
            ).label("negotiation_status"),
        )
        .join(AdRequest, AdRequest.campaign_id == Campaign.campaign_id)
        .outerjoin(Negotiation, Negotiation.ad_request_id == AdRequest.ad_request_id)
        .join(Sponsor, Sponsor.sponsor_id == Campaign.sponsor_id)  # Join with Sponsor
        .filter(AdRequest.influencer_id == influencer_id)
        .all()
    )

    # Prepare data from the query result
    data = []
    for campaign in campaigns:
        campaign_data = {
            "campaign_id": campaign.campaign_id,
            "campaign_name": campaign.campaign_name,
            "description": campaign.description,
            "goals": campaign.goals,
            "niche": campaign.niche,
            "sponsor_id": campaign.sponsor_id,
            "sponsor_name": campaign.sponsor_name,  # Add sponsor name
            "start_date": (
                campaign.start_date.strftime("%Y/%m/%d")
                if campaign.start_date
                else None
            ),
            "end_date": (
                campaign.end_date.strftime("%Y/%m/%d") if campaign.end_date else None
            ),
            "ad_request_id": campaign.ad_request_id,
            "influencer_id": campaign.influencer_id,
            "messages": campaign.messages,
            "payment_amount": str(campaign.payment_amount),
            "requirements": campaign.requirements,
            "status": campaign.status,
            "negotiated_amount": str(campaign.negotiated_amount),
            "negotiation_status": campaign.negotiation_status,
            "negotiation_id": campaign.negotiation_id,
        }
        data.append(campaign_data)

    return data
