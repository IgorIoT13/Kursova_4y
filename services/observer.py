from abc import ABC, abstractmethod
from typing import Any, List


class ProductObserver(ABC):
    @abstractmethod
    def notify(self, product_id: int, payload: Any) -> None:
        """Called when a product event occurs (e.g., becomes available)."""


class ProductPublisher(ABC):
    @abstractmethod
    def attach(self, observer: ProductObserver) -> None:
        raise NotImplementedError

    @abstractmethod
    def detach(self, observer: ProductObserver) -> None:
        raise NotImplementedError

    @abstractmethod
    def notify_all(self, product_id: int, payload: Any) -> None:
        raise NotImplementedError


class UserAvailabilityObserver(ProductObserver):
    """Example observer which would notify a user when product becomes available.

    For now it only records notifications to an internal list so tests can assert
    behavior; later this can integrate with real notification channels.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.notifications: List[dict] = []

    def notify(self, product_id: int, payload: Any) -> None:
        # In future: push real notification (email/push). For now, record it.
        self.notifications.append({'user_id': self.user_id, 'product_id': product_id, 'payload': payload})
