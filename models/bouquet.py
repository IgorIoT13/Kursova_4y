"""Bouquet model."""
from datetime import datetime, timezone


def init_bouquet_model(db, Flower, Wrapping, BouquetType):
    class Bouquet(db.Model):
        __tablename__ = 'bouquets'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=True, unique=True)

        # Each Bouquet references one Flower, one Wrapping and one BouquetType
        flower_id = db.Column(db.Integer, db.ForeignKey('flowers.id'), nullable=True)
        wrapping_id = db.Column(db.Integer, db.ForeignKey('wrappings.id'), nullable=True)
        type_id = db.Column(db.Integer, db.ForeignKey('bouquet_types.id'), nullable=True)

        # Relationships to parent models (many Bouquets can reference same parent)
        flower = db.relationship('Flower', back_populates='bouquets', foreign_keys=[flower_id])
        wrapping = db.relationship('Wrapping', back_populates='bouquets', foreign_keys=[wrapping_id])
        type = db.relationship('BouquetType', back_populates='bouquets', foreign_keys=[type_id])

        flowers_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        def __repr__(self):
            return f"<Bouquet {self.id}>"

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'wrapping': self.wrapping.to_dict() if self.wrapping else None,
                'flower': self.flower.to_dict() if self.flower else None,
                'type': self.type.to_dict() if self.type else None,
                'flowers_count': self.flowers_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    return Bouquet


# placeholder
Bouquet = None
