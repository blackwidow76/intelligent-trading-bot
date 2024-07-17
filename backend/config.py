import os
from dotenv import load_dotenv

from service import App

# Load environment variables from .env file
load_dotenv()


class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pumpportal')  # Default value if not set
    PUMPPORTAL_API_URL = os.getenv('PUMPPORTAL_API_URL', 'wss://pumpportal.fun/api/data')
    PUMPPORTAL_API_KEY = os.getenv('PUMPPORTAL_API_KEY')
    PUMPPORTAL_PUBLIC_KEY = os.getenv('PUMPPORTAL_PUBLIC_KEY')
    PUMPPORTAL_PRIVATE_KEY = os.getenv('PUMPPORTAL_PRIVATE_KEY')
