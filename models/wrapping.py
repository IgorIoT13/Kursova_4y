"""Wrapping model."""
from datetime import datetime


def init_wrapping_model(db):
    class Wrapping(db.Model):
        __tablename__ = 'wrappings'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        price = db.Column(db.Numeric(10, 2), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Wrapping {self.name}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'price': float(self.price) if self.price is not None else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return Wrapping


# placeholder
Wrapping = None
