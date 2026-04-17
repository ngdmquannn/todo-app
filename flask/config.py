import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    DEBUG = False

    # VULN #8 (kept) — CSRF protection disabled
    # Left off because the app is a JWT-bearer SPA; an attacker who already
    # has a valid token (stolen via XSS in a partner site or via CORS) can
    # still forge state-changing requests. SAST rarely flags a *missing*
    # config key, which is why this slips through.
    WTF_CSRF_ENABLED = False
