from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt
from flask import flash

db = SQLAlchemy()
bcrypt = Bcrypt()


def initialize_database(app):
    """
    Initializes the database by creating all tables.
    This function should be called when the app starts.
    """
    with app.app_context():
        db.create_all()  # Creates the tables


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)  # unique
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # unique
    role = db.Column(db.Enum("admin", "sponsor", "influencer"), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    login_date = db.Column(db.TIMESTAMP, default=None, onupdate=db.func.current_timestamp())

    sponsors = db.relationship("Sponsor", backref="user", lazy=True)
    influencers = db.relationship("Influencer", backref="user", lazy=True)
    user_flags = db.relationship(
        "UserFlag", foreign_keys="UserFlag.flagged_by", backref="flagger", lazy=True
    )
    flagged_by_user_flags = db.relationship(
        "UserFlag", foreign_keys="UserFlag.user_id", backref="flagged_user", lazy=True
    )
    campaign_flags = db.relationship(
        "CampaignFlag",
        foreign_keys="CampaignFlag.flagged_by",
        backref="flagger",
        lazy=True,
    )

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Sponsor(db.Model):
    __tablename__ = "sponsors"

    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    company_name = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    budget = db.Column(db.Numeric(10, 2))
    company_description = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)

    campaigns = db.relationship("Campaign", backref="sponsor", lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Influencer(db.Model):
    __tablename__ = "influencers"

    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String(255))
    category = db.Column(db.String(255))
    niche = db.Column(db.String(255))
    reach = db.Column(db.Integer)
    description = db.Column(db.String(255))

    ad_requests = db.relationship("AdRequest", backref="influencer", lazy=True)
    negotiations = db.relationship("Negotiation", backref="influencer", lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Campaign(db.Model):
    __tablename__ = "campaigns"

    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey("sponsors.sponsor_id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    visibility = db.Column(db.Enum("public", "private"), default="public")
    goals = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(255), nullable=False)

    ad_requests = db.relationship(
        "AdRequest", backref="campaign", lazy=True, cascade="all, delete-orphan"
    )
    campaign_flags = db.relationship(
        "CampaignFlag", backref="campaign", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @validates("end_date")
    def validate_end_date(self, key, end_date):
        if self.start_date and end_date:
            if end_date < self.start_date:
                flash("End date must be greater than start date", "error")
        return end_date


class AdRequest(db.Model):
    __tablename__ = "ad_requests"

    ad_request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.campaign_id"), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey("influencers.influencer_id"), nullable=False)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum("pending", "accepted", "rejected", "negotiation"), default="pending")
    messages = db.Column(db.Text)

    negotiations = db.relationship("Negotiation", backref="ad_request", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Negotiation(db.Model):
    __tablename__ = "negotiations"

    negotiation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey("ad_requests.ad_request_id"), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey("influencers.influencer_id"), nullable=False)
    proposed_payment_amount = db.Column(db.Numeric(10, 2))
    negotiation_status = db.Column(db.Enum("pending", "accepted", "rejected"), default="pending")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserFlag(db.Model):
    __tablename__ = "user_flags"

    flag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flagged_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CampaignFlag(db.Model):
    __tablename__ = "campaign_flags"

    flag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flagged_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.campaign_id"), nullable=False)
    reason = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def init_db(app):
    with app.app_context():
        db.create_all()

        # Check if the database already contains data
        if not User.query.filter_by(role="admin").first():
            # Add dummy data
            admin = User(
                username="admin",
                email="admin@example.com",
                role="admin",
            )
            admin.set_password("password")
            db.session.add(admin)
            db.session.commit()

            sponsor = User(
                username="sponsor",
                email="sponsor@example.com",
                role="sponsor",
            )
            sponsor.set_password("password")
            db.session.add(sponsor)
            db.session.commit()

            influencer = User(
                username="influencer",
                email="influencer@example.com",
                role="influencer",
            )
            influencer.set_password("password")
            db.session.add(influencer)
            db.session.commit()

            sponsor_data = Sponsor(
                user_id=sponsor.user_id,
                company_name="Sponsor Company",
                industry="Technology",
                budget=10000.00,
                company_description="Tech Company focusing on innovation."
            )
            influencer_data = Influencer(
                user_id=influencer.user_id,
                name="Influencer Name",
                category="Lifestyle",
                niche="Travel",
                reach=5000,
                description="Travel influencer with a focus on adventure tourism."
            )

            db.session.add(sponsor_data)
            db.session.add(influencer_data)
            db.session.commit()

            campaign = Campaign(
                sponsor_id=sponsor_data.sponsor_id,
                name="Campaign 1",
                description="Description of campaign 1",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                budget=5000.00,
                visibility="public",
                goals="Increase brand awareness",
                niche="health",
            )

            db.session.add(campaign)
            db.session.commit()

            ad_request = AdRequest(
                campaign_id=campaign.campaign_id,
                influencer_id=influencer_data.influencer_id,
                requirements="Influencer should create 3 posts per week",
                payment_amount=1000.00,
                status="pending",
                messages="Looking forward to collaborating!"
            )

            db.session.add(ad_request)
            db.session.commit()

            # Optional: add a negotiation entry for the ad request
            negotiation = Negotiation(
                ad_request_id=ad_request.ad_request_id,
                influencer_id=influencer_data.influencer_id,
                proposed_payment_amount=1200.00,
                negotiation_status="pending"
            )

            db.session.add(negotiation)
            db.session.commit()
