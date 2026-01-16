"""Wrapping model."""
from datetime import datetime, timezone


def init_wrapping_model(db):
    class Wrapping(db.Model):
        __tablename__ = 'wrappings'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        price = db.Column(db.Numeric(10, 2), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        # One-to-many: a wrapping can be used in many bouquets
        bouquets = db.relationship('Bouquet', back_populates='wrapping', lazy=True)

        def __repr__(self):
            return f"<Wrapping {self.name}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'price': float(self.price) if self.price is not None else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'bouquets': [b.id for b in self.bouquets]
            }

    return Wrapping


# placeholder
Wrapping = None
