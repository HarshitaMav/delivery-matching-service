from app.services.geo import haversine_km


def test_haversine_zero_distance() -> None:
    assert haversine_km(40.7128, -74.0060, 40.7128, -74.0060) == 0


def test_haversine_nyc_to_philadelphia() -> None:
    # NYC to Philadelphia is about 130 km.
    distance = haversine_km(40.7128, -74.0060, 39.9526, -75.1652)
    assert 120 < distance < 140
