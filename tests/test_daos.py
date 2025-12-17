from dao.base_dao import BaseDAO
from dao.flower_dao import FlowerDAO
from dao.wrapping_dao import WrappingDAO
from dao.bouquet_type_dao import BouquetTypeDAO
from dao.bouquet_dao import BouquetDAO

from models import Flower, Wrapping, BouquetType, Bouquet


def test_flower_crud(session):
    dao = FlowerDAO(Flower, session)
    f = dao.create(name='Rose', price=10.5)
    assert f.id is not None
    got = dao.get(f.id)
    assert got.name == 'Rose'
    all_items = dao.list()
    assert any(i.id == f.id for i in all_items)
    updated = dao.update(f.id, name='Tulip')
    assert updated.name == 'Tulip'
    assert dao.delete(f.id) is True
    assert dao.get(f.id) is None


def test_wrapping_crud(session):
    dao = WrappingDAO(Wrapping, session)
    w = dao.create(name='Paper', price=1.0)
    assert w.id is not None
    assert dao.get(w.id).name == 'Paper'
    items = dao.list()
    assert any(i.id == w.id for i in items)
    dao.update(w.id, name='Foil')
    assert dao.get(w.id).name == 'Foil'
    assert dao.delete(w.id) is True


def test_type_crud(session):
    dao = BouquetTypeDAO(BouquetType, session)
    t = dao.create(type='Anniversary')
    assert t.id is not None
    assert dao.get(t.id).type == 'Anniversary'
    dao.update(t.id, type='Birthday')
    assert dao.get(t.id).type == 'Birthday'
    assert dao.delete(t.id) is True


def test_bouquet_crud(session):
    # create parent records first
    fdao = FlowerDAO(Flower, session)
    wdao = WrappingDAO(Wrapping, session)
    tdao = BouquetTypeDAO(BouquetType, session)
    flower = fdao.create(name='Lily', price=5.0)
    wrap = wdao.create(name='Cloth', price=2.0)
    btype = tdao.create(type='Wedding')

    dao = BouquetDAO(Bouquet, session)
    b = dao.create(name='Bouquet A', flower_id=flower.id, wrapping_id=wrap.id, type_id=btype.id, flowers_count=3)
    assert b.id is not None
    assert dao.get(b.id).name == 'Bouquet A'
    items = dao.list()
    assert any(i.id == b.id for i in items)
    dao.update(b.id, name='Bouquet B')
    assert dao.get(b.id).name == 'Bouquet B'
    assert dao.delete(b.id) is True

