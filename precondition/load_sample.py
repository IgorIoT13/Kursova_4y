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

from models import db, Flower, Wrapping, BouquetType, Bouquet
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from dao.bouquet_dao import BouquetDAO
from flask import Flask
from config import config


def create_app_for_precondition():
    cfg_name = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config[cfg_name])
    db.init_app(app)
    return app


SAMPLE_FLOWERS = [
    {'name': 'Rose', 'price': 5.0},
    {'name': 'Tulip', 'price': 3.0},
    {'name': 'Lily', 'price': 4.5},
]

SAMPLE_WRAPPINGS = [
    {'name': 'Paper', 'price': 1.0},
    {'name': 'Cloth', 'price': 2.5},
]

SAMPLE_TYPES = [
    {'type': 'Birthday'},
    {'type': 'Wedding'},
]


def load_sample(auto_commit: bool = True) -> List[int]:
    """Load sample data and return created Bouquet ids."""
    app = create_app_for_precondition()
    created_ids = []
    with app.app_context():
        # Create tables if missing
        db.create_all()
        session = db.session
        fdao = FlowerDAO(Flower, session)
        wdao = WrappingDAO(Wrapping, session)
        tdao = BouquetTypeDAO(BouquetType, session)
        bdao = BouquetDAO(Bouquet, session)

        flowers = [fdao.create(**f) for f in SAMPLE_FLOWERS]
        wrappings = [wdao.create(**w) for w in SAMPLE_WRAPPINGS]
        types = [tdao.create(**t) for t in SAMPLE_TYPES]

        # create a bouquet for each combination
        for f in flowers:
            i=0
            for w in wrappings:
                for t in types:
                    i+=1
                    b = bdao.create(name=f"{f.name} combo_{i}", flower_id=f.id, wrapping_id=w.id, type_id=t.id, flowers_count=3)
                    created_ids.append(b.id)

    return created_ids


if __name__ == '__main__':
    ids = load_sample()
    print('Created bouquets:', ids)
