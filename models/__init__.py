"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import model initializers
from models.flower import init_flower_model
from models.wrapping import init_wrapping_model
from models.bouquet_type import init_bouquet_type_model
from models.bouquet import init_bouquet_model
from models.position import init_position_model
from models.user_type import init_user_type_model
from models.user import init_user_model
from models.delivery import init_delivery_model
from models.order import init_order_model

# Initialize models after db is defined
Flower = init_flower_model(db)
Wrapping = init_wrapping_model(db)
BouquetType = init_bouquet_type_model(db)
Bouquet = init_bouquet_model(db, Flower, Wrapping, BouquetType)
Position = init_position_model(db, Bouquet)
UserType = init_user_type_model(db)
User = init_user_model(db, UserType)
Delivery = init_delivery_model(db)
Order = init_order_model(db, User, Position, Delivery)

__all__ = ['db', 'Flower', 'Wrapping', 'BouquetType', 'Bouquet', 'Position', 'UserType', 'User', 'Delivery', 'Order']
