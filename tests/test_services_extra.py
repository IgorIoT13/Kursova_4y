from services.flower_service import FlowerService
from services.wrapping_service import WrappingService
from services.bouquet_type_service import BouquetTypeService
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from models import Flower, Wrapping, BouquetType


def test_flower_service_crud_and_filters(session):
    fdao = FlowerDAO(None, session)
    fdao.model = Flower

    service = FlowerService(session)

    # create
    f = service.create('F1', 1.25)
    assert f.id is not None
    assert f.name == 'F1'

    # get and get_by_name
    got = service.get(f.id)
    assert got.id == f.id
    byname = service.get_by_name('F1')
    assert byname.id == f.id

    # list with price filters
    f2 = service.create('F2', 2.50)
    all_items = service.list()
    assert any(i.id == f.id for i in all_items)
    filtered = service.list(min_price=2.0)
    assert all(i.price >= 2.0 for i in filtered)

    # update
    updated = service.update(f.id, name='F1-up', price=1.5)
    assert updated.name == 'F1-up'

    # delete
    assert service.delete(f2.id) is True
    assert service.get(f2.id) is None


def test_wrapping_service_crud_and_filters(session):
    wdao = WrappingDAO(None, session)
    wdao.model = Wrapping

    service = WrappingService(session)

    w = service.create('W1', 0.75)
    assert w.id is not None
    assert w.name == 'W1'

    assert service.get(w.id).id == w.id
    assert service.get_by_name('W1').id == w.id

    w2 = service.create('W2', 1.25)
    filtered = service.list(max_price=1.0)
    assert all(i.price <= 1.0 for i in filtered)

    updated = service.update(w.id, name='W1-new')
    assert updated.name == 'W1-new'

    assert service.delete(w2.id) is True


def test_bouquet_type_service_crud(session):
    tdao = BouquetTypeDAO(None, session)
    tdao.model = BouquetType

    service = BouquetTypeService(session)

    t = service.create('TypeA')
    assert t.id is not None
    assert t.type == 'TypeA'

    assert service.get(t.id).id == t.id
    assert service.get_by_name('TypeA').id == t.id

    t2 = service.create('TypeB')
    items = service.list()
    assert any(i.id == t.id for i in items)

    updated = service.update(t.id, type='TypeA-new')
    assert updated.type == 'TypeA-new'

    assert service.delete(t2.id) is True
