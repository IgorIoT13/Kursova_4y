from typing import Optional, List
from dao.bouquet_type_dao import BouquetTypeDAO
from models import BouquetType


class BouquetTypeService:
    def __init__(self, session):
        self.session = session
        self.dao = BouquetTypeDAO(None, session)

    def create(self, type_name: str, **extra):
        self.dao.model = BouquetType
        if type_name:
            existing = self.session.query(BouquetType).filter(BouquetType.type == type_name).first()
            if existing:
                raise ValueError(f"BouquetType '{type_name}' already exists")
        return self.dao.create(type=type_name, **extra)

    def get(self, type_id: int):
        self.dao.model = BouquetType
        return self.dao.get(type_id)

    def get_by_name(self, type_name: str):
        self.dao.model = BouquetType
        return self.session.query(BouquetType).filter(BouquetType.type == type_name).first()

    def list(self, limit: int = 100, offset: int = 0) -> List[BouquetType]:
        self.dao.model = BouquetType
        return self.dao.list(limit=limit, offset=offset)

    def update(self, type_id: int, **fields):
        self.dao.model = BouquetType
        if 'type' in fields and fields['type']:
            t = fields['type']
            q = self.session.query(BouquetType).filter(BouquetType.type == t, BouquetType.id != type_id)
            if self.session.query(q.exists()).scalar():
                raise ValueError(f"BouquetType '{t}' already exists")
        return self.dao.update(type_id, **fields)

    def delete(self, type_id: int):
        self.dao.model = BouquetType
        return self.dao.delete(type_id)
