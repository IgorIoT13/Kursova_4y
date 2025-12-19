from dao.notification_dao import NotificationDAO


class NotificationService:
    def __init__(self, session):
        self.session = session
        self.dao = NotificationDAO(None, session)

    def create(self, user_id: int, bouquet_id: int = None, message: str = None):
        from models import Notification as _Notification
        self.dao.model = _Notification
        return self.dao.create(user_id=user_id, bouquet_id=bouquet_id, message=message)

    def list_for_user(self, user_id: int):
        from models import Notification as _Notification
        return self.session.query(_Notification).filter_by(user_id=user_id).order_by(_Notification.created_at.desc()).all()

    def mark_read(self, notification_id: int):
        from models import Notification as _Notification
        self.dao.model = _Notification
        return self.dao.update(notification_id, read=True)
