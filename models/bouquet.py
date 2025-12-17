"""Bouquet model."""
from datetime import datetime


def init_bouquet_model(db, Flower, Wrapping, BouquetType):
    class Bouquet(db.Model):
        __tablename__ = 'bouquets'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=True)

        # One-to-many relationships: children hold FK to bouquets
        flowers = db.relationship('Flower', backref='bouquet', lazy=True)
        types = db.relationship('BouquetType', backref='bouquet', lazy=True)
        wrappings = db.relationship('Wrapping', backref='bouquet', lazy=True)

        flowers_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Bouquet {self.id}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'wrappings': [w.to_dict() for w in self.wrappings],
                'flowers': [f.to_dict() for f in self.flowers],
                'types': [t.to_dict() for t in self.types],
                'flowers_count': self.flowers_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return Bouquet


# placeholder
Bouquet = None
