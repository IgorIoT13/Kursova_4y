from dao.order_dao import OrderDAO
from dao.position_dao import PositionDAO
from services.card_service import CardService


class OrderService:
    def __init__(self, session):
        self.session = session
        self.dao = OrderDAO(None, session)
        self.position_dao = PositionDAO(None, session)

    def create(self, user_id: int, position_id: int, delivery_id: int, quantity: int, user_card_name: str = 'standard'):
        # Ensure DAOs have their models bound to avoid caller setup
        from models import Order as _OrderModel, Position as _PositionModel, Delivery as _DeliveryModel
        self.dao.model = _OrderModel
        self.position_dao.model = _PositionModel

        pos = self.position_dao.get(position_id)
        if not pos:
            return None
        available = pos.quantity or 0
        to_buy = max(0, min(quantity, available))
        if to_buy == 0:
            # nothing to buy
            return None

        # compute base total: position.price * to_buy
        base_total = float(pos.price) * to_buy

        # apply card strategy
        strategy = CardService.get_strategy(user_card_name)
        total_after_price = base_total * strategy.price_factor(base_total)

        # delivery price: fetch Delivery model via session
        delivery_obj = self.session.get(_DeliveryModel, delivery_id)
        delivery_cost = 0.0
        if delivery_obj is not None:
            delivery_cost = float(getattr(delivery_obj, 'price', 0.0)) * strategy.delivery_factor(float(getattr(delivery_obj, 'price', 0.0)))

        final_total = total_after_price + delivery_cost

        # create order record
        order = self.dao.create(user_id=user_id, position_id=position_id, delivery_id=delivery_id, quantity=to_buy, total_price=final_total)

        # decrement position stock
        new_q = max(0, available - to_buy)
        self.position_dao.update(position_id, quantity=new_q)

        return order

    def get(self, order_id: int):
        return self.dao.get(order_id)

    def delete(self, order_id: int):
        # when deleting, restore position quantity
        from models import Order as _OrderModel, Position as _PositionModel
        self.dao.model = _OrderModel
        self.position_dao.model = _PositionModel

        order = self.dao.get(order_id)
        if not order:
            return False
        # restore qty
        try:
            pos = self.position_dao.get(order.position_id)
            if pos:
                self.position_dao.update(pos.id, quantity=pos.quantity + order.quantity)
        except Exception:
            pass
        return self.dao.delete(order_id)

    def increment_one(self, order_id: int):
        """Add one unit to the order if position has stock; adjust price using user's card."""
        from models import Order as _OrderModel, Position as _PositionModel, User as _UserModel
        self.dao.model = _OrderModel
        self.position_dao.model = _PositionModel

        order = self.dao.get(order_id)
        if not order:
            return None

        pos = self.position_dao.get(order.position_id)
        if not pos or (pos.quantity or 0) <= 0:
            return None

        # determine user's card
        user_obj = self.session.get(_UserModel, order.user_id) if hasattr(self.session, 'get') else None
        card_name = getattr(user_obj, 'card', 'standard') if user_obj is not None else 'standard'
        strategy = CardService.get_strategy(card_name)

        # unit price after card
        unit_price = float(pos.price) * strategy.price_factor(float(pos.price))

        # update order
        new_qty = order.quantity + 1
        new_total = float(order.total_price) + unit_price
        updated = self.dao.update(order_id, quantity=new_qty, total_price=new_total)

        # decrement position
        self.position_dao.update(pos.id, quantity=pos.quantity - 1)
        return updated

    def decrement_one(self, order_id: int):
        """Remove one unit from the order; if it becomes zero, delete the order and restore stock."""
        from models import Order as _OrderModel, Position as _PositionModel
        self.dao.model = _OrderModel
        self.position_dao.model = _PositionModel

        order = self.dao.get(order_id)
        if not order:
            return None

        if order.quantity <= 1:
            # deleting will restore quantity
            self.delete(order_id)
            return None

        pos = self.position_dao.get(order.position_id)
        # determine user's card for price adjustment
        try:
            user_obj = self.session.get(__import__('models').models.User, order.user_id)
        except Exception:
            user_obj = None
        card_name = getattr(user_obj, 'card', 'standard') if user_obj is not None else 'standard'
        strategy = CardService.get_strategy(card_name)

        unit_price = float(pos.price) * strategy.price_factor(float(pos.price)) if pos else 0.0

        new_qty = order.quantity - 1
        new_total = float(order.total_price) - unit_price
        updated = self.dao.update(order_id, quantity=new_qty, total_price=new_total)

        # restore one to position
        if pos:
            self.position_dao.update(pos.id, quantity=pos.quantity + 1)

        return updated
