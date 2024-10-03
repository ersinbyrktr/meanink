# app/config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CORS_HEADERS = 'Content-Type'


config = Config()
