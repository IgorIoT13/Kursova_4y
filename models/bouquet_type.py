"""BouquetType model."""


def init_bouquet_type_model(db):
    class BouquetType(db.Model):
        __tablename__ = 'bouquet_types'
        id = db.Column(db.Integer, primary_key=True)
        # Many-to-one: many types may belong to one bouquet
        bouquet_id = db.Column(db.Integer, db.ForeignKey('bouquets.id'), nullable=True)
        type = db.Column(db.String(120), nullable=False)

        def __repr__(self):
            return f"<BouquetType {self.type}>"

        def to_dict(self):
            return {
                'id': self.id,
                'type': self.type
            }

    return BouquetType


# placeholder
BouquetType = None
