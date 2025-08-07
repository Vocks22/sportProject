"""Database configuration for DietTracker"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parents[3] / 'config' / 'development.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # API Configuration
    API_PREFIX = os.environ.get('API_PREFIX', '/api')
    # Ajouter les domaines Netlify et localhost
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 
        'http://localhost:5173,http://localhost:3000,http://localhost:5000,https://diettracker-front.netlify.app').split(',')
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Database
    db_path = Path(__file__).resolve().parents[1] / 'database' / 'diettracker_dev.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    # Logging
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    FLASK_ENV = 'testing'
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # JWT
    JWT_ACCESS_TOKEN_EXPIRES = 60  # 1 minute for testing
    
    # Logging
    LOG_LEVEL = 'INFO'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Database - Use PostgreSQL in production
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Render utilise postgres:// mais SQLAlchemy veut postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).resolve().parents[1] / 'database' / 'diettracker_prod.db')
    
    # Security - Avec valeurs par défaut temporaires pour le déploiement initial
    SECRET_KEY = os.environ.get('SECRET_KEY', 'temp-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'temp-jwt-secret-change-in-production')
    
    # Avertissement si les clés par défaut sont utilisées
    if SECRET_KEY == 'temp-secret-key-change-in-production':
        print("WARNING: Using default SECRET_KEY - Please set in production!")
    if JWT_SECRET_KEY == 'temp-jwt-secret-change-in-production':
        print("WARNING: Using default JWT_SECRET_KEY - Please set in production!")
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration object by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config[config_name]