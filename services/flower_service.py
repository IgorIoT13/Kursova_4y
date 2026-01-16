from typing import Optional, List
from dao.flower_dao import FlowerDAO
from models import Flower


class FlowerService:
    def __init__(self, session):
        self.session = session
        self.dao = FlowerDAO(None, session)

    def create(self, name: str, price, **extra):
        self.dao.model = Flower
        # ensure no duplicate name at service level
        if name:
            existing = self.session.query(Flower).filter(Flower.name == name).first()
            if existing:
                raise ValueError(f"Flower with name '{name}' already exists")
        return self.dao.create(name=name, price=price, **extra)

    def get(self, flower_id: int):
        self.dao.model = Flower
        return self.dao.get(flower_id)

    def get_price(self, flower_id: int):
        """Return numeric price for a flower by id, or None if not found."""
        self.dao.model = Flower
        f = self.dao.get(flower_id)
        if not f:
            return None
        return float(f.price) if f.price is not None else None

    def get_by_name(self, name: str):
        self.dao.model = Flower
        return self.session.query(Flower).filter(Flower.name == name).first()

    def list(self, min_price: Optional[float] = None, max_price: Optional[float] = None, limit: int = 100, offset: int = 0) -> List[Flower]:
        self.dao.model = Flower
        q = self.session.query(Flower).order_by(Flower.id)
        if min_price is not None:
            q = q.filter(Flower.price >= min_price)
        if max_price is not None:
            q = q.filter(Flower.price <= max_price)
        return q.limit(limit).offset(offset).all()

    def update(self, flower_id: int, **fields):
        self.dao.model = Flower
        if 'name' in fields and fields['name']:
            name = fields['name']
            q = self.session.query(Flower).filter(Flower.name == name, Flower.id != flower_id)
            if self.session.query(q.exists()).scalar():
                raise ValueError(f"Flower with name '{name}' already exists")
        return self.dao.update(flower_id, **fields)

    def delete(self, flower_id: int):
        self.dao.model = Flower
        return self.dao.delete(flower_id)
