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

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
