from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from dao.bouquet_dao import BouquetDAO
from dao.position_dao import PositionDAO
from dao.delivery_dao import DeliveryDAO

from services.position_service import PositionService
from services.order_service import OrderService
from services.delivery_service import DeliveryService

from models import Flower, Wrapping, BouquetType, Bouquet, Position, Delivery


def test_order_creation_and_discount_and_stock(session):
    # create components
    fdao = FlowerDAO(Flower, session)
    wdao = WrappingDAO(Wrapping, session)
    tdao = BouquetTypeDAO(BouquetType, session)
    f = fdao.create(name='OFlow', price=5.0)
    w = wdao.create(name='OWrap', price=2.0)
    bt = tdao.create(type='OBT')

    bdao = BouquetDAO(Bouquet, session)
    b = bdao.create(name='OrderBouq', flower_id=f.id, wrapping_id=w.id, type_id=bt.id, flowers_count=2)

    # create position
    pdao = PositionDAO(Position, session)
    pos = pdao.create(bouquet_id=b.id, price=12.0, quantity=5)

    # create delivery
    ddao = DeliveryDAO(Delivery, session)
    d = ddao.create(method='Courier', price=3.0)

    # now create order service
    oservice = OrderService(session)
    oservice.dao.model = None  # will be set by tests as needed
    oservice.position_dao.model = Position
    oservice.dao.model = None

    # create order with social card (10% off price, delivery same)
    order = oservice.create(user_id=1, position_id=pos.id, delivery_id=d.id, quantity=2, user_card_name='social')
    assert order is not None
    # base = pos.price*2 = 24, after 10% = 21.6, delivery 3 -> total 24.6
    assert abs(float(order.total_price) - 24.6) < 1e-6

    # position quantity decreased from 5 to 3
    pos_after = oservice.position_dao.get(pos.id)
    assert pos_after.quantity == 3

    # create order with gold card (10% off and free delivery)
    order2 = oservice.create(user_id=2, position_id=pos.id, delivery_id=d.id, quantity=3, user_card_name='gold')
    # base = 12*3 = 36, after 10% = 32.4, delivery free -> 32.4
    assert abs(float(order2.total_price) - 32.4) < 1e-6

    # position now 0
    pos_final = oservice.position_dao.get(pos.id)
    assert pos_final.quantity == 0

    # deleting order restores quantity
    oservice.dao.model = None
    # manual delete via service (the DAO binding will be used inside method)
    # find order id
    assert oservice.delete(order2.id) is True
    restored = oservice.position_dao.get(pos.id)
    assert restored.quantity == 3


def test_increment_decrement_one(session):
    # setup nearly identical to previous: create bouquet and position
    fdao = FlowerDAO(Flower, session)
    wdao = WrappingDAO(Wrapping, session)
    tdao = BouquetTypeDAO(BouquetType, session)
    f = fdao.create(name='IncF', price=4.0)
    w = wdao.create(name='IncW', price=1.0)
    bt = tdao.create(type='IncBT')
    bdao = BouquetDAO(Bouquet, session)
    b = bdao.create(name='IncBouq', flower_id=f.id, wrapping_id=w.id, type_id=bt.id, flowers_count=1)
    pdao = PositionDAO(Position, session)
    pos = pdao.create(bouquet_id=b.id, price=6.0, quantity=1)
    ddao = DeliveryDAO(Delivery, session)
    d = ddao.create(method='Post', price=2.0)

    # create an order of 1
    oservice = OrderService(session)
    oservice.dao.model = None
    oservice.position_dao.model = Position
    order = oservice.create(user_id=5, position_id=pos.id, delivery_id=d.id, quantity=1, user_card_name='standard')
    assert order is not None

    # increment one -> but pos quantity is 0 so increment should return None
    inc = oservice.increment_one(order.id)
    assert inc is None

    # restore one to position so increment works
    pdao.update(pos.id, quantity=1)
    inc2 = oservice.increment_one(order.id)
    assert inc2.quantity == 2

    # decrement one -> should reduce to 1
    dec = oservice.decrement_one(order.id)
    assert dec is not None
    assert dec.quantity == 1

    # decrement one again -> should delete order
    res = oservice.decrement_one(order.id)
    assert res is None
