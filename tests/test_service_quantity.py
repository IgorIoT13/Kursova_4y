from builders.general_bouquet import GeneralBouquet
from services.bouquet_service import BouquetService
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO


def test_purchase_and_restock(session):
    # create parents
    fdao = FlowerDAO(None, session)
    wdao = WrappingDAO(None, session)
    tdao = BouquetTypeDAO(None, session)
    from models import Flower, Wrapping, BouquetType
    fdao.model = Flower
    wdao.model = Wrapping
    tdao.model = BouquetType

    flower = fdao.create(name='QFlower', price=2.0)
    wrapping = wdao.create(name='QWrap', price=1.0)
    btype = tdao.create(type='QType')

    # create bouquet with quantity 5
    builder = GeneralBouquet()
    builder.set_name('QtyBouquet').set_flower(flower.id).set_wrapping(wrapping.id).set_type(btype.id).set_flowers_count(3).set_quantity(5)
    service = BouquetService(session)
    b = service.create_from_builder(builder)
    assert b.quantity == 5

    # purchase 2 -> quantity 3
    service.purchase(b.id, qty=2)
    got = service.get(b.id)
    assert got.quantity == 3

    # purchase 5 -> quantity 0 (not negative)
    service.purchase(b.id, qty=5)
    got = service.get(b.id)
    assert got.quantity == 0

    # restock 10 -> quantity 10
    service.restock(b.id, qty=10)
    got = service.get(b.id)
    assert got.quantity == 10
