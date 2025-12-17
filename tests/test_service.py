from builders.general_bouquet import GeneralBouquet
from services.bouquet_service import BouquetService
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO


def test_bouquet_service_create(session):
    # create parent records
    fdao = FlowerDAO(None, session)
    wdao = WrappingDAO(None, session)
    tdao = BouquetTypeDAO(None, session)
    # bind models
    from models import Flower, Wrapping, BouquetType
    fdao.model = Flower
    wdao.model = Wrapping
    tdao.model = BouquetType

    flower = fdao.create(name='TestFlower', price=1.0)
    wrapping = wdao.create(name='TestWrap', price=0.5)
    btype = tdao.create(type='TestType')

    # build bouquet
    builder = GeneralBouquet()
    builder.set_name('SvcBouquet').set_flower(flower.id).set_wrapping(wrapping.id).set_type(btype.id).set_flowers_count(2)

    service = BouquetService(session)
    b = service.create_from_builder(builder)
    assert b is not None
    assert b.name == 'SvcBouquet'
    # get/list
    got = service.get(b.id)
    assert got.id == b.id
    items = service.list()
    assert any(i.id == b.id for i in items)

    # update
    updated = service.update(b.id, name='SvcBouquet2')
    assert updated.name == 'SvcBouquet2'

    # delete
    assert service.delete(b.id) is True
    assert service.get(b.id) is None
