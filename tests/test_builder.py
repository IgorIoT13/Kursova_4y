from builders.general_bouquet import GeneralBouquet


def test_general_bouquet_build():
    b = GeneralBouquet()
    b.reset().set_name('Test').set_flower(1).set_wrapping(2).set_type(3).set_flowers_count(5)
    data = b.build()
    assert isinstance(data, dict)
    assert data['name'] == 'Test'
    assert data['flower_id'] == 1
    assert data['wrapping_id'] == 2
    assert data['type_id'] == 3
    assert data['flowers_count'] == 5
