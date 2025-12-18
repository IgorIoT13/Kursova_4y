from typing import Optional
from dao.position_dao import PositionDAO
from services.observer import ProductObserver


class PositionService:
    """Service to manage shop positions (listings) for bouquets.

    Responsibilities:
    - create positions from a Bouquet object
    - manage quantity (set/add/remove)
    - compute listing price based on bouquet composition
    - notify attached observers on significant events
    """

    def __init__(self, session):
        self.session = session
        self.dao = PositionDAO(None, session)
        self._observers: list[ProductObserver] = []

    def attach(self, obs: ProductObserver):
        if obs not in self._observers:
            self._observers.append(obs)

    def detach(self, obs: ProductObserver):
        if obs in self._observers:
            self._observers.remove(obs)

    def _notify(self, position_id: int, payload: dict):
        for o in list(self._observers):
            try:
                o.notify(position_id, payload)
            except Exception:
                # swallow observer errors for now
                pass

    def create_from_bouquet(self, bouquet, price: Optional[float] = None, quantity: int = 0):
        """Create a Position for a bouquet; if price omitted compute from bouquet."""
    # caller should set self.dao.model to Position before calling create
        listing_price = price if price is not None else self.compute_price_from_bouquet(bouquet)
        obj = self.dao.create(bouquet_id=bouquet.id, price=listing_price, quantity=quantity)
        # notify if created with quantity
        if quantity > 0:
            self._notify(obj.id, {'event': 'created_with_stock', 'quantity': quantity})
        return obj

    # Standard CRUD methods to route through the service
    def create(self, **fields):
        return self.dao.create(**fields)

    def get(self, position_id: int):
        return self.dao.get(position_id)

    def list(self, limit: int = 100, offset: int = 0):
        return self.dao.list(limit=limit, offset=offset)

    def update(self, position_id: int, **fields):
        return self.dao.update(position_id, **fields)

    def delete(self, position_id: int):
        return self.dao.delete(position_id)

    def set_quantity(self, position_id: int, value: int):
        obj = self.dao.get(position_id)
        if not obj:
            return None
        prev = obj.quantity
        obj = self.dao.update(position_id, quantity=value)
        # notify when stock becomes available
        if prev <= 0 and value > 0:
            self._notify(position_id, {'event': 'stock_available', 'quantity': value})
        return obj

    def add_quantity(self, position_id: int, delta: int):
        if delta <= 0:
            return self.dao.get(position_id)
        obj = self.dao.get(position_id)
        if not obj:
            return None
        new_q = obj.quantity + delta
        obj = self.dao.update(position_id, quantity=new_q)
        if obj.quantity > 0:
            self._notify(position_id, {'event': 'stock_added', 'quantity': delta})
        return obj

    def remove_quantity(self, position_id: int, delta: int):
        if delta <= 0:
            return self.dao.get(position_id)
        obj = self.dao.get(position_id)
        if not obj:
            return None
        new_q = max(0, obj.quantity - delta)
        obj = self.dao.update(position_id, quantity=new_q)
        if obj.quantity == 0:
            self._notify(position_id, {'event': 'stock_depleted'})
        return obj

    def compute_price_from_bouquet(self, bouquet) -> float:
        """Compute price for a Position based on bouquet's components.

        Simple rule: total = flower.price * flowers_count + wrapping.price
        (Assumes bouquet.flower and bouquet.wrapping are populated)
        """
        flower = getattr(bouquet, 'flower', None)
        wrapping = getattr(bouquet, 'wrapping', None)
        count = getattr(bouquet, 'flowers_count', 0) or 0
        total = 0.0
        if flower and getattr(flower, 'price', None) is not None:
            total += float(flower.price) * count
        if wrapping and getattr(wrapping, 'price', None) is not None:
            total += float(wrapping.price)
        return total
