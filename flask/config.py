import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ["headers"]
    # VULN #2 — weak/default JWT secret (CWE-798, CWE-521)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESG_TOKEN_EXPIRES = timedelta(days=30)

    # VULN #8 — CSRF protection disabled (CWE-352)
    WTF_CSRF_ENABLED = False

    # VULN — debug mode on in production (CWE-489)
    DEBUG = True
