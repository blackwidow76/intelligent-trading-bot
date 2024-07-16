import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PUMPPORTAL_API_URL = os.getenv('PUMPPORTAL_API_URL', 'wss://pumpportal.fun/api/data')
    PUMPPORTAL_API_KEY = os.getenv('PUMPPORTAL_API_KEY')

config = Config()