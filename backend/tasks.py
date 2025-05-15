import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from celery import Celery
from flask import Flask, render_template
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
from models import db, User, AdRequest, Sponsor, Campaign
import csv
import os

# Initialize Flask and Celery
application = Flask(__name__)
application.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Use Redis as the broker
application.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
application.config['MAIL_SERVER'] = 'smtp://localhost:1025'  # Mailhog SMTP server
application.config['MAIL_PORT'] = 1025  # Mailhog default port
application.config['MAIL_USE_TLS'] = False  # No TLS needed for Mailhog

application.config['MAIL_USE_SSL'] = False  # No SSL needed for Mailhog
application.config['MAIL_USERNAME'] = None  # No username required for Mailhog
application.config['MAIL_PASSWORD'] = None  # No password required for Mailhog
application.config['MAIL_DEFAULT_SENDER']='mankojp23@example.com'
# Initialize Flask-Mail
mail = Mail(application)

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(application)

# Function to send email using Flask-Mail (Mailhog for testing)
def send_mail(to, subject, html):
    msg = Message(
        subject=subject,
        sender=application.config['MAIL_DEFAULT_SENDER'],
        recipients=[to],
        body=html
    )
    try:
        mail.send(msg)
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Error sending email to {to}: {str(e)}")

# Celery task to send daily reminders to influencers
@celery.task
def send_daily_reminders():
    with application.app_context():
        current_time = datetime.now(timezone(timedelta(hours=6, minutes=30))).date()

        # Query influencers who haven't logged in today or have never logged in
        users = User.query.filter(
            User.role == 'influencer',
            (User.login_date == None) | (User.login_date < current_time)
        ).all()

        for user in users:
            pending_ad_requests = AdRequest.query.filter_by(influencer_id=user.user_id, status='pending').all()
            if pending_ad_requests:
                subject = "Daily Reminder: Visit the App"
                body = f"Dear {user.username}, please visit the app to manage your pending ad requests."
                send_mail(user.email, subject, body)

# Celery task to send monthly reports to sponsors
@celery.task
def send_monthly_report():
    with application.app_context():
        try:
            sponsors = Sponsor.query.all()
            report_data = []

            for sponsor in sponsors:
                campaigns = Campaign.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
                total_requests = 0
                accepted_requests = 0
                rejected_requests = 0
                pending_requests = 0

                for campaign in campaigns:
                    ad_requests = AdRequest.query.filter_by(campaign_id=campaign.campaign_id).all()
                    total_requests += len(ad_requests)
                    for request in ad_requests:
                        if request.status == 'accepted':
                            accepted_requests += 1
                        elif request.status == 'rejected':
                            rejected_requests += 1
                        elif request.status == 'pending':
                            pending_requests += 1

                report_data.append({
                    'sponsor': sponsor.company,
                    'total_requests': total_requests,
                    'accepted_requests': accepted_requests,
                    'rejected_requests': rejected_requests,
                    'pending_requests': pending_requests
                })

            # Generate the monthly report CSV
            report_file_path = '/path/to/reports/monthly_report.csv'
            with open(report_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['sponsor', 'total_requests', 'accepted_requests', 'rejected_requests', 'pending_requests'])
                writer.writeheader()
                for data in report_data:
                    writer.writerow(data)

            # Send the report to each sponsor
            for sponsor in sponsors:
                msg = Message(
                    subject="Monthly Report: Ad Requests Overview",
                    sender="Influencia@example.com",
                    recipients=[sponsor.contact_email],
                    body=f"Dear {sponsor.company},\n\nAttached is your monthly report of ad requests for your campaigns."
                )
                try:
                    with open(report_file_path, 'rb') as fp:
                        msg.attach('monthly_report.csv', 'text/csv', fp.read())
                    mail.send(msg)
                    print(f"Monthly report sent to {sponsor.company}")
                except Exception as e:
                    print(f"Error sending email to {sponsor.company}: {str(e)}")
        except Exception as ex:
            print(f"Error in monthly report task: {str(ex)}")

# Celery task to export campaign data to CSV
@celery.task
def export_campaign_data():
    with application.app_context():
        try:
            campaigns = Campaign.query.all()
            campaign_data = []

            for campaign in campaigns:
                campaign_data.append({
                    'title': campaign.title,
                    'description': campaign.campaign_description,
                    'start': campaign.start.strftime('%Y-%m-%d'),
                    'end': campaign.end.strftime('%Y-%m-%d'),
                    'visibility': campaign.visibility,
                    'budget': campaign.campaign_budget
                })

            export_file_path = '/path/to/reports/campaign_data.csv'
            with open(export_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['title', 'description', 'start', 'end', 'visibility', 'budget'])
                writer.writeheader()
                for data in campaign_data:
                    writer.writerow(data)

            print(f"Campaign data successfully exported to {export_file_path}")
        except Exception as ex:
            print(f"Error in exporting campaign data: {str(ex)}")
