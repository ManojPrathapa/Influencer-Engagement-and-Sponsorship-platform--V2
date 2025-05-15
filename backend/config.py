from flask_caching import Cache
from datetime import timedelta
from celery.schedules import crontab

class AppConfig:
    # Secret Key for Flask
    SECRET_KEY = "your_secret_key_here"

    # SQLAlchemy configuration for SQLite
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"  # Update as per your database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis Cache configuration
    CACHE_TYPE = 'redis'  # Use Redis for caching
    CACHE_DEFAULT_TIMEOUT = 100
    CACHE_KEY_PREFIX = 'myprefix'
    CACHE_REDIS_URL = "redis://localhost:6379/1"  # Redis server URL

    # Flask-Mail configuration for email sending (update with real credentials)
    MAIL_SERVER = 'smtp://localhost:1025'  # Use Mailhog for testing emails
    MAIL_PORT = 1025  # Default Mailhog port
    MAIL_USE_TLS = False  # No need for TLS with Mailhog
    MAIL_USE_SSL = False  # No need for SSL with Mailhog
    MAIL_USERNAME = None  # No authentication required for Mailhog
    MAIL_PASSWORD = None  # No password required for Mailhog

    MAIL_DEFAULT_SENDER = 'mankojp23@example.com'  # Default sender email address (optional)

    # Celery configuration for background tasks
    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as the message broker
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Redis for storing task results
    CELERY_TIMEZONE = 'Asia/Kolkata'  # Adjust timezone as needed
    CELERY_BEAT_SCHEDULE = {
        'send-daily-reminders': {
            'task': 'tasks.send_daily_reminders',  # Task function to call
            'schedule': crontab(minute=4, hour=3),  # Run at 8 AM daily
        },
        'send-monthly-report': {
            'task': 'tasks.send_monthly_report',  # Task function to call
            'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run on the 1st of each month at midnight
        },
    }

    CELERY_INCLUDE = ['tasks']  # Task module import for Celery to discover tasks

# Initialize the Cache instance
cache = Cache()
