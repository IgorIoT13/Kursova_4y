"""Base DAO with common CRUD helpers."""
from typing import Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class BaseDAO:
    def __init__(self, model: Type, session: Session):
        self.model = model
        self.session = session

    def create(self, **fields):
        obj = self.model(**fields)
        self.session.add(obj)
        try:
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except IntegrityError:
            self.session.rollback()
            raise

    def get(self, obj_id) -> Optional[object]:
        return self.session.get(self.model, obj_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[object]:
        return self.session.query(self.model).order_by(self.model.id).limit(limit).offset(offset).all()

    def update(self, obj_id, **fields):
        obj = self.get(obj_id)
        if not obj:
            return None
        for k, v in fields.items():
            setattr(obj, k, v)
        try:
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except IntegrityError:
            self.session.rollback()
            raise

    def delete(self, obj_id) -> bool:
        obj = self.get(obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.commit()
        return True
