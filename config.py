import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration class with default values and environment variable overrides
class Config:
    # MongoDB settings
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/tea_processing')
    
    # Secret key for session
    SECRET_KEY = os.getenv('SECRET_KEY', 'tea-processing-monitor-secret-key')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = os.getenv('TESTING', 'False').lower() in ('true', '1', 't')
    
    # Set to True to skip database initialization on startup (useful for production)
    SKIP_DB_INIT = os.getenv('SKIP_DB_INIT', 'False').lower() in ('true', '1', 't')
