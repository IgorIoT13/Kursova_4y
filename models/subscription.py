"""Subscription model: user subscribes to bouquet availability notifications."""
from datetime import datetime, timezone


def init_subscription_model(db, User, Bouquet):
    class Subscription(db.Model):
        __tablename__ = 'subscriptions'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        bouquet_id = db.Column(db.Integer, db.ForeignKey('bouquets.id'), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        __table_args__ = (
            db.UniqueConstraint('user_id', 'bouquet_id', name='uq_user_bouquet_sub'),
        )

        def to_dict(self):
            return {'id': self.id, 'user_id': self.user_id, 'bouquet_id': self.bouquet_id, 'created_at': self.created_at.isoformat()}

    return Subscription
