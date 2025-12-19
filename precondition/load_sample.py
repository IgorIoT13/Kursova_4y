"""Script to load sample/precondition data into the database.

Usage:
    # run manually from project root
    python -m precondition.load_sample

Optional environment variable to auto-run during app startup (not enabled by default):
    PRECONDITION_AUTOLOAD=true

This script is intentionally safe: it uses SQLAlchemy models and DAOs and prints progress.
"""
import os
from typing import List

# project import path helper
import sys
sys.path.append(r'C:\WorkspaceFolder\Projects\Kursova_4y')

from models import db, Flower, Wrapping, BouquetType, Bouquet, Position, UserType, User, Delivery, Order
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from dao.bouquet_dao import BouquetDAO
from dao.position_dao import PositionDAO
from dao.delivery_dao import DeliveryDAO
from flask import Flask
from config import config


def create_app_for_precondition():
    cfg_name = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config[cfg_name])
    db.init_app(app)
    return app


SAMPLE_FLOWERS = [
    {'name': 'Chip', 'price': 1.0},
    {'name': 'Rose', 'price': 5.0},
    {'name': 'Tulip', 'price': 3.0},
    {'name': 'Lily', 'price': 4.5},
    {'name': 'Carnation', 'price': 2.5},
    {'name': 'Orchid', 'price': 6.0},
    {'name': 'Peony', 'price': 7.0},
    {'name': 'Daisy', 'price': 1.5},
    {'name': 'Sunflower', 'price': 2.0},
]

SAMPLE_WRAPPINGS = [
    {'name': 'Paper', 'price': 1.0},
    {'name': 'Cloth', 'price': 2.5},
    {'name': 'Foil', 'price': 1.8},
    {'name': 'Basket', 'price': 4.0},
]

SAMPLE_TYPES = [
    {'type': 'Birthday'},
    {'type': 'Wedding'},
    {'type': 'Anniversary'},
    {'type': 'Romantic'},
    {'type': 'Sympathy'},
]


def load_sample(auto_commit: bool = True) -> List[int]:
    """Load sample data and return created Bouquet ids."""
    app = create_app_for_precondition()
    created_ids = []
    with app.app_context():
        # Create tables if missing
        db.create_all()
        session = db.session
        # DAOs
        fdao = FlowerDAO(Flower, session)
        wdao = WrappingDAO(Wrapping, session)
        tdao = BouquetTypeDAO(BouquetType, session)
        bdao = BouquetDAO(Bouquet, session)
        utdao = None
        # user DAOs (optional, may not exist in older repo states)
        try:
            from dao.user_type_dao import UserTypeDAO
            from dao.user_dao import UserDAO
            utdao = UserTypeDAO(UserType, session)
            udao = UserDAO(User, session)
        except Exception:
            udao = None

        # other DAOs
        posdao = PositionDAO(Position, session)
        ddao = DeliveryDAO(Delivery, session)
        odao = None
        try:
            from dao.order_dao import OrderDAO
            odao = OrderDAO(Order, session)
        except Exception:
            odao = None

        # create sample parents
        flowers = [fdao.create(**f) for f in SAMPLE_FLOWERS]
        wrappings = [wdao.create(**w) for w in SAMPLE_WRAPPINGS]
        types = [tdao.create(**t) for t in SAMPLE_TYPES]

        # create some user types and users
        users = []
        if utdao is not None and udao is not None:
            admin_type = utdao.create(name='Admin', is_admin=True)
            regular_type = utdao.create(name='Customer', is_admin=False)
            # users with different cards
            users.append(udao.create(name='admin', password='admin', card='standard', user_type_id=admin_type.id))
            users.append(udao.create(name='alice', password='alicepass', card='standard', user_type_id=regular_type.id))
            users.append(udao.create(name='bob', password='bobpass', card='social', user_type_id=regular_type.id))
            users.append(udao.create(name='carol', password='carolpass', card='gold', user_type_id=regular_type.id))

        # create bouquets (mixes) and positions
        i = 0
        for flower in flowers:
            for wrapping in wrappings:
                for btype in types:
                    i += 1
                    name = f"{flower.name} {btype.type} #{i}"
                    b = bdao.create(name=name, flower_id=flower.id, wrapping_id=wrapping.id, type_id=btype.id, flowers_count=(i % 5) + 1)
                    created_ids.append(b.id)
                    # position price computed from components, with slight markup
                    base_price = float(flower.price) * b.flowers_count + float(wrapping.price)
                    price = round(base_price * (1.0 + (i % 3) * 0.05), 2)
                    qty = (i % 10) + 1
                    posdao.create(bouquet_id=b.id, price=price, quantity=qty)

        # create deliveries
        deliveries = [ddao.create(method='Courier', price=4.0), ddao.create(method='Pickup', price=0.0), ddao.create(method='Postal', price=2.5)]

        # create a few sample orders using OrderDAO if available
        if odao is not None and len(created_ids) >= 3:
            # pick first position
            first_position = session.query(Position).first()
            if first_position:
                # create a sample order for alice if exists
                if udao is not None and len(users) > 1:
                    odao.create(user_id=users[1].id, position_id=first_position.id, delivery_id=deliveries[0].id, quantity=1, total_price=float(first_position.price) + float(deliveries[0].price))

    print('Created:', len(created_ids), 'bouquets,', len(flowers), 'flowers,', len(wrappings), 'wrappings')

    return created_ids


if __name__ == '__main__':
    ids = load_sample()
    print('Created bouquets:', ids)
