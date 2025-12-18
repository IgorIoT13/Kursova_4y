"""Position model initializer - represents a shop listing for a bouquet."""
from datetime import datetime, timezone


def init_position_model(db, bouquet_model):
    class Position(db.Model):
        __tablename__ = 'positions'

        id = db.Column(db.Integer, primary_key=True)
        bouquet_id = db.Column(db.Integer, db.ForeignKey('bouquets.id'), nullable=False)
        bouquet = db.relationship(bouquet_model, backref='positions')
        price = db.Column(db.Numeric(10, 2), nullable=False)
        quantity = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        def __repr__(self):
            return f"<Position {self.id} for bouquet {self.bouquet_id}>"

        def to_dict(self):
            return {
                'id': self.id,
                'bouquet_id': self.bouquet_id,
                'price': float(self.price) if self.price is not None else None,
                'quantity': self.quantity,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    return Position


# placeholder
Position = None
