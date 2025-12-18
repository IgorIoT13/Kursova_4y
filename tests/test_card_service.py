from services.card_service import (
    CardService,
    StandardCard,
    SocialCard,
    GoldCard,
)


def test_standard_card():
    s = StandardCard()
    assert s.price_factor(100) == 1.0
    assert s.delivery_factor(10) == 1.0
    # pricing application is responsibility of higher-level code
    assert s.price_factor(100) * 100 + s.delivery_factor(10) * 10 == 110.0


def test_social_card():
    s = SocialCard()
    assert s.price_factor(200) == 0.9
    assert s.delivery_factor(5) == 1.0
    assert s.price_factor(200) * 200 + s.delivery_factor(5) * 5 == 200*0.9 + 5


def test_gold_card():
    s = GoldCard()
    assert s.price_factor(50) == 0.9
    assert s.delivery_factor(8) == 0.0
    assert s.price_factor(50) * 50 + s.delivery_factor(8) * 8 == 50*0.9


def test_factory_lookup():
    assert isinstance(CardService.get_strategy('standard'), StandardCard)
    assert isinstance(CardService.get_strategy('social'), SocialCard)
    assert isinstance(CardService.get_strategy('gold'), GoldCard)
    # unknown falls back to Standard
    assert isinstance(CardService.get_strategy('unknown'), StandardCard)
