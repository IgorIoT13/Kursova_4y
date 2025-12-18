import pytest
from builders.general_bouquet import GeneralBouquet
from services.bouquet_service import BouquetService
from services.flower_service import FlowerService
from services.wrapping_service import WrappingService
from services.bouquet_type_service import BouquetTypeService
from models import Flower, Wrapping, BouquetType

def test_bouquet_service_create(session):
    # create parent records
    fsvc = FlowerService(session)
    wsvc = WrappingService(session)
    tsvc = BouquetTypeService(session)

    flower = fsvc.create('TestFlower', 1.0)
    wrapping = wsvc.create('TestWrap', 0.5)
    btype = tsvc.create('TestType')

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


def test_unique_name_create_and_update(session):
    fsvc = FlowerService(session)
    wsvc = WrappingService(session)
    tsvc = BouquetTypeService(session)

    flower = fsvc.create('UFlower', 1.0)
    wrapping = wsvc.create('UWrap', 1.0)
    btype = tsvc.create('UType')

    service = BouquetService(session)

    # create first bouquet
    b1_builder = GeneralBouquet().set_name('Unique').set_flower(flower.id).set_wrapping(wrapping.id).set_type(btype.id)
    b1 = service.create_from_builder(b1_builder)
    assert b1.name == 'Unique'

    # creating another with same name should raise
    b2_builder = GeneralBouquet().set_name('Unique').set_flower(flower.id).set_wrapping(wrapping.id).set_type(btype.id)
    with pytest.raises(ValueError):
        service.create_from_builder(b2_builder)

    # create second with different name
    b3_builder = GeneralBouquet().set_name('Unique2').set_flower(flower.id).set_wrapping(wrapping.id).set_type(btype.id)
    b3 = service.create_from_builder(b3_builder)

    # attempt to update b3 name to 'Unique' should raise
    with pytest.raises(ValueError):
        service.update(b3.id, name='Unique')