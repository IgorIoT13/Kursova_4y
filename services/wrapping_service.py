from typing import Optional, List
from dao.wrapping_dao import WrappingDAO
from models import Wrapping


class WrappingService:
    def __init__(self, session):
        self.session = session
        self.dao = WrappingDAO(None, session)

    def create(self, name: str, price, **extra):
        self.dao.model = Wrapping
        if name:
            existing = self.session.query(Wrapping).filter(Wrapping.name == name).first()
            if existing:
                raise ValueError(f"Wrapping with name '{name}' already exists")
        return self.dao.create(name=name, price=price, **extra)

    def get(self, wrapping_id: int):
        self.dao.model = Wrapping
        return self.dao.get(wrapping_id)

    def get_price(self, wrapping_id: int):
        """Return numeric price for a wrapping by id, or None if not found."""
        self.dao.model = Wrapping
        w = self.dao.get(wrapping_id)
        if not w:
            return None
        return float(w.price) if w.price is not None else None

    def get_by_name(self, name: str):
        self.dao.model = Wrapping
        return self.session.query(Wrapping).filter(Wrapping.name == name).first()

    def list(self, min_price: Optional[float] = None, max_price: Optional[float] = None, limit: int = 100, offset: int = 0) -> List[Wrapping]:
        self.dao.model = Wrapping
        q = self.session.query(Wrapping).order_by(Wrapping.id)
        if min_price is not None:
            q = q.filter(Wrapping.price >= min_price)
        if max_price is not None:
            q = q.filter(Wrapping.price <= max_price)
        return q.limit(limit).offset(offset).all()

    def update(self, wrapping_id: int, **fields):
        self.dao.model = Wrapping
        if 'name' in fields and fields['name']:
            name = fields['name']
            q = self.session.query(Wrapping).filter(Wrapping.name == name, Wrapping.id != wrapping_id)
            if self.session.query(q.exists()).scalar():
                raise ValueError(f"Wrapping with name '{name}' already exists")
        return self.dao.update(wrapping_id, **fields)

    def delete(self, wrapping_id: int):
        self.dao.model = Wrapping
        return self.dao.delete(wrapping_id)
