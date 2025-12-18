"""User model initializer."""
from datetime import datetime, timezone


def init_user_model(db, user_type_model):
    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        password = db.Column(db.String(255), nullable=False)
        card = db.Column(db.String(60), nullable=True)  # strategy name stored as string
        user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'), nullable=True)
        user_type = db.relationship(user_type_model, backref='users')
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        def __repr__(self):
            return f"<User {self.name}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'card': self.card,
                'user_type_id': self.user_type_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    return User


# placeholder
User = None
