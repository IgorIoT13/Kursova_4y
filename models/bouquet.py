"""Bouquet model."""
from datetime import datetime


def init_bouquet_model(db, Flower, Wrapping, BouquetType):
    # Association tables
    bouquet_flowers = db.Table(
        'bouquet_flowers',
        db.Column('bouquet_id', db.Integer, db.ForeignKey('bouquets.id'), primary_key=True),
        db.Column('flower_id', db.Integer, db.ForeignKey('flowers.id'), primary_key=True)
    )

    bouquet_types = db.Table(
        'bouquet_types_assoc',
        db.Column('bouquet_id', db.Integer, db.ForeignKey('bouquets.id'), primary_key=True),
        db.Column('type_id', db.Integer, db.ForeignKey('bouquet_types.id'), primary_key=True)
    )

    class Bouquet(db.Model):
        __tablename__ = 'bouquets'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=True)
        wrapping_id = db.Column(db.Integer, db.ForeignKey('wrappings.id'), nullable=True)
        wrapping = db.relationship('Wrapping', backref=db.backref('bouquets', lazy=True))

        # many-to-many with Flower
        flowers = db.relationship('Flower', secondary=bouquet_flowers, lazy='subquery', backref=db.backref('bouquets', lazy=True))

        # many-to-many with BouquetType
        types = db.relationship('BouquetType', secondary=bouquet_types, lazy='subquery', backref=db.backref('bouquets', lazy=True))

        flowers_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Bouquet {self.id}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'wrapping': self.wrapping.to_dict() if self.wrapping else None,
                'flowers': [f.to_dict() for f in self.flowers],
                'types': [t.to_dict() for t in self.types],
                'flowers_count': self.flowers_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return Bouquet


# placeholder
Bouquet = None
