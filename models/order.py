"""Order model initializer."""
from datetime import datetime, timezone


def init_order_model(db, user_model, position_model, delivery_model):
    class Order(db.Model):
        __tablename__ = 'orders'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
        delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False)
        quantity = db.Column(db.Integer, nullable=False, default=1)
        total_price = db.Column(db.Numeric(12, 2), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        user = db.relationship(user_model, backref='orders')
        position = db.relationship(position_model, backref='orders')
        delivery = db.relationship(delivery_model, backref='orders')

        def __repr__(self):
            return f"<Order {self.id} user={self.user_id} pos={self.position_id}>"

        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'position_id': self.position_id,
                'delivery_id': self.delivery_id,
                'quantity': self.quantity,
                'total_price': float(self.total_price),
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    return Order


# placeholder
Order = None
