"""BouquetType model."""


def init_bouquet_type_model(db):
    class BouquetType(db.Model):
        __tablename__ = 'bouquet_types'
        id = db.Column(db.Integer, primary_key=True)

        # One-to-many: a bouquet type can be used in many bouquets
        type = db.Column(db.String(120), nullable=False)
        bouquets = db.relationship('Bouquet', back_populates='type', lazy=True)

        def __repr__(self):
            return f"<BouquetType {self.type}>"

        def to_dict(self):
            return {
                'id': self.id,
                'type': self.type,
                'bouquets': [b.id for b in self.bouquets]
            }

    return BouquetType


# placeholder
BouquetType = None
