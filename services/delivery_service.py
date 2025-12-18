from dao.delivery_dao import DeliveryDAO


class DeliveryService:
    def __init__(self, session):
        self.session = session
        self.dao = DeliveryDAO(None, session)

    def create(self, method: str, price):
        return self.dao.create(method=method, price=price)

    def get(self, delivery_id: int):
        return self.dao.get(delivery_id)

    def list(self, limit: int = 100, offset: int = 0):
        return self.dao.list(limit=limit, offset=offset)

    def update(self, delivery_id: int, **fields):
        return self.dao.update(delivery_id, **fields)

    def delete(self, delivery_id: int):
        return self.dao.delete(delivery_id)
