"""
Database initialization module
Centralizes SQLAlchemy instance creation
"""

from flask_sqlalchemy import SQLAlchemy

# Single instance of SQLAlchemy to be shared across the application
db = SQLAlchemy()