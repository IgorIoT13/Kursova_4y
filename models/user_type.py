"""UserType model initializer."""


def init_user_type_model(db):
    class UserType(db.Model):
        __tablename__ = 'user_types'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)

        def __repr__(self):
            return f"<UserType {self.name}>"

        def to_dict(self):
            return {'id': self.id, 'name': self.name, 'is_admin': bool(self.is_admin)}

    return UserType


# placeholder
UserType = None
