from typing import Dict, Optional
from builders.general_bouquet import GeneralBouquet
from dao.bouquet_dao import BouquetDAO
from models import Bouquet

class BouquetService:
    def __init__(self, session):
        self.session = session
        self.dao = BouquetDAO(None, session)  # model will be bound when used

    def create_from_builder(self, builder: GeneralBouquet):
        data = builder.build()
        # create DAO with actual model import to avoid circulars
        self.dao.model = Bouquet
        return self.dao.create(**data)

    def get(self, bouquet_id: int):
        self.dao.model = Bouquet
        return self.dao.get(bouquet_id)

    def list(self, limit: int = 100, offset: int = 0):
        self.dao.model = Bouquet
        return self.dao.list(limit=limit, offset=offset)

    def update(self, bouquet_id: int, **fields):
        self.dao.model = Bouquet
        return self.dao.update(bouquet_id, **fields)

    def delete(self, bouquet_id: int):
        self.dao.model = Bouquet
        return self.dao.delete(bouquet_id)
