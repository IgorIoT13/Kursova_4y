from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from dao.bouquet_dao import BouquetDAO
from dao.position_dao import PositionDAO

from services.position_service import PositionService
from services.observer import UserAvailabilityObserver

from models import Flower, Wrapping, BouquetType, Bouquet, Position


def test_position_service_quantity_and_price(session):
    # prepare parents
    fdao = FlowerDAO(Flower, session)
    wdao = WrappingDAO(Wrapping, session)
    tdao = BouquetTypeDAO(BouquetType, session)
    f = fdao.create(name='TestF', price=2.0)
    w = wdao.create(name='TestW', price=1.5)
    bt = tdao.create(type='TestBT')

    # create bouquet
    bdao = BouquetDAO(Bouquet, session)
    b = bdao.create(name='PosBouq', flower_id=f.id, wrapping_id=w.id, type_id=bt.id, flowers_count=3)

    # create position using DAO binding
    pdao = PositionDAO(Position, session)
    service = PositionService(session)
    service.dao.model = Position

    # create position from bouquet
    pos = service.create_from_bouquet(b, quantity=0)
    assert pos is not None

    # compute price should be flower.price*count + wrapping.price = 2*3 + 1.5 = 7.5
    computed = service.compute_price_from_bouquet(b)
    assert abs(computed - 7.5) < 1e-6

    # set quantity and observe notifications
    obs = UserAvailabilityObserver(user_id=100)
    service.attach(obs)

    # set from 0 to 5 -> triggers stock_available
    updated = service.set_quantity(pos.id, 5)
    assert updated.quantity == 5
    assert any(n['payload'].get('event') == 'stock_available' for n in obs.notifications)

    # add quantity
    prev_len = len(obs.notifications)
    service.add_quantity(pos.id, 2)
    assert any(n['payload'].get('event') == 'stock_added' for n in obs.notifications[prev_len:])

    # remove more than available to deplete
    service.remove_quantity(pos.id, 100)
    assert service.dao.get(pos.id).quantity == 0
    assert any(n.get('payload', {}).get('event') == 'stock_depleted' for n in obs.notifications)


def test_compute_price_ignores_cards(session):
    # create components
    fdao = FlowerDAO(Flower, session)
    wdao = WrappingDAO(Wrapping, session)
    tdao = BouquetTypeDAO(BouquetType, session)
    f = fdao.create(name='ComputeF', price=3.0)
    w = wdao.create(name='ComputeW', price=2.0)
    bt = tdao.create(type='ComputeBT')

    bdao = BouquetDAO(Bouquet, session)
    b = bdao.create(name='ComputeBouq', flower_id=f.id, wrapping_id=w.id, type_id=bt.id, flowers_count=4)

    service = PositionService(session)
    # expected: flower.price * flowers_count + wrapping.price = 3*4 + 2 = 14
    assert abs(service.compute_price_from_bouquet(b) - 14.0) < 1e-6

