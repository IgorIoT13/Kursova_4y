"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to make them available at package level
from models.user import User

__all__ = ['db', 'User']
