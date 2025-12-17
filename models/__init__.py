"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import and initialize models after db is defined
from models.user import init_user_model
User = init_user_model(db)

__all__ = ['db', 'User']
