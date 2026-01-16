from dao.subscription_dao import SubscriptionDAO


class SubscriptionService:
    def __init__(self, session):
        self.session = session
        self.dao = SubscriptionDAO(None, session)

    def subscribe(self, user_id: int, bouquet_id: int):
        from models import Subscription as _Sub
        self.dao.model = _Sub
        try:
            return self.dao.create(user_id=user_id, bouquet_id=bouquet_id)
        except Exception:
            # likely duplicate or integrity error -> return existing if any
            return self.session.query(_Sub).filter_by(user_id=user_id, bouquet_id=bouquet_id).first()

    def unsubscribe(self, user_id: int, bouquet_id: int):
        from models import Subscription as _Sub
        self.dao.model = _Sub
        sub = self.session.query(_Sub).filter_by(user_id=user_id, bouquet_id=bouquet_id).first()
        if not sub:
            return False
        return self.dao.delete(sub.id)

    def list_for_bouquet(self, bouquet_id: int):
        from models import Subscription as _Sub
        return self.session.query(_Sub).filter_by(bouquet_id=bouquet_id).all()

    def list_for_user(self, user_id: int):
        from models import Subscription as _Sub
        return self.session.query(_Sub).filter_by(user_id=user_id).all()
