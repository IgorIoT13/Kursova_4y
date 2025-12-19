"""Notification model to persist subscription notifications."""
from datetime import datetime, timezone


def init_notification_model(db, User, Bouquet):
    class Notification(db.Model):
        __tablename__ = 'notifications'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        bouquet_id = db.Column(db.Integer, db.ForeignKey('bouquets.id'), nullable=True)
        message = db.Column(db.String(255), nullable=True)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        read = db.Column(db.Boolean, default=False)

        def to_dict(self):
            return {'id': self.id, 'user_id': self.user_id, 'bouquet_id': self.bouquet_id, 'message': self.message, 'created_at': self.created_at.isoformat(), 'read': self.read}

    return Notification
