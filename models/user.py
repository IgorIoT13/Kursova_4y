"""User model."""
from datetime import datetime


def init_user_model(db):
    """Initialize User model with db instance."""
    
    class User(db.Model):
        """Example User model."""
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<User {self.username}>'
        
        def to_dict(self):
            """Convert user object to dictionary."""
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    return User


# This will be set by __init__.py after db is created
User = None
