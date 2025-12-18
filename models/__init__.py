"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import model initializers
from models.flower import init_flower_model
from models.wrapping import init_wrapping_model
from models.bouquet_type import init_bouquet_type_model
from models.bouquet import init_bouquet_model
from models.user_type import init_user_type_model
from models.user import init_user_model

# Initialize models after db is defined
Flower = init_flower_model(db)
Wrapping = init_wrapping_model(db)
BouquetType = init_bouquet_type_model(db)
Bouquet = init_bouquet_model(db, Flower, Wrapping, BouquetType)
UserType = init_user_type_model(db)
User = init_user_model(db, UserType)

__all__ = ['db', 'Flower', 'Wrapping', 'BouquetType', 'Bouquet', 'UserType', 'User']
