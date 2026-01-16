"""Delivery model initializer."""
from datetime import datetime, timezone


def init_delivery_model(db):
    class Delivery(db.Model):
        __tablename__ = 'deliveries'

        id = db.Column(db.Integer, primary_key=True)
        method = db.Column(db.String(120), nullable=False)
        price = db.Column(db.Numeric(10, 2), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        def __repr__(self):
            return f"<Delivery {self.method}>"

        def to_dict(self):
            return {'id': self.id, 'method': self.method, 'price': float(self.price)}

    return Delivery


# placeholder
Delivery = None
