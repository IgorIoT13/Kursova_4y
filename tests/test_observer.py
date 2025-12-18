from services.observer import UserAvailabilityObserver


def test_user_availability_observer_records_notification():
    obs = UserAvailabilityObserver(user_id=42)
    assert obs.notifications == []

    obs.notify(product_id=7, payload={'available': True})
    assert len(obs.notifications) == 1
    n = obs.notifications[0]
    assert n['user_id'] == 42
    assert n['product_id'] == 7
    assert n['payload']['available'] is True
