"""
Configuration Example
Copy this to config.py and customize as needed
"""
import os

class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Camera Configuration
    CAMERA_URL = os.environ.get('CAMERA_URL', 'http://10.0.0.197:8080/cam_c')
    CAPTURE_INTERVAL = float(os.environ.get('CAPTURE_INTERVAL', '1.0'))  # seconds
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    OPENAI_MAX_TOKENS = 10  # For True/False responses
    OPENAI_TEMPERATURE = 0  # Deterministic responses
    
    # Storage Configuration
    FRAME_STORAGE_BASE = 'exp_time'
    FRAME_FORMAT = 'JPEG'
    FRAME_QUALITY = 95
    
    # Update Intervals (milliseconds)
    FRAME_UPDATE_INTERVAL = 2000  # Frontend frame refresh
    FILTER_UPDATE_INTERVAL = 3000  # Frontend filter refresh
    FILTER_EVAL_INTERVAL = 1.0  # Backend filter evaluation (seconds)
    
    # Performance Settings
    MAX_CONCURRENT_FILTERS = 10  # Limit number of filters
    REQUEST_TIMEOUT = 5  # Camera request timeout (seconds)
    
    # UI Configuration
    DEFAULT_THEME = 'light'  # 'light' or 'dark'
    ENABLE_CHAT = True
    

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here
    

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    CAMERA_URL = 'http://localhost:8080/test_cam'  # Mock camera for testing
    

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env='default'):
    """Get configuration based on environment"""
    return config.get(env, config['default'])

