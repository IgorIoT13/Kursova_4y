"""Flower model."""
from datetime import datetime


def init_flower_model(db):
    class Flower(db.Model):
        __tablename__ = 'flowers'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        price = db.Column(db.Numeric(10, 2), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        # One-to-many: a flower can be used in many bouquets
        bouquets = db.relationship('Bouquet', back_populates='flower', lazy=True)

        def __repr__(self):
            return f"<Flower {self.name}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'price': float(self.price) if self.price is not None else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'bouquets': [b.id for b in self.bouquets]
            }

    return Flower


# placeholder for import-time name binding from models.__init__
Flower = None
