import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import application models and db
import sys
sys.path.append(r'C:\WorkspaceFolder\Projects\Kursova_4y')
from models import db as models_db, Flower, Wrapping, BouquetType, Bouquet


@pytest.fixture(scope='session')
def engine():
    # Use SQLite in-memory for tests
    engine = create_engine('sqlite:///:memory:')
    return engine


@pytest.fixture(scope='session')
def tables(engine):
    # bind a new metadata to engine
    models_db.metadata.create_all(bind=engine)
    yield
    models_db.metadata.drop_all(bind=engine)


@pytest.fixture()
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
