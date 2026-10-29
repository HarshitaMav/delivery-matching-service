from types import SimpleNamespace

from app.services.matcher import GeoPoint, nearest_neighbors


def test_nearest_neighbor_picks_closest_driver() -> None:
    pickup = GeoPoint(lat=40.7580, lng=-73.9855)  # Times Square
    drivers = [
        SimpleNamespace(id=1, lat=40.7306, lng=-73.9352),  # East Village-ish, farther
        SimpleNamespace(id=2, lat=40.7589, lng=-73.9851),  # almost at pickup
        SimpleNamespace(id=3, lat=40.6782, lng=-73.9442),  # Brooklyn, farthest
    ]

    result = nearest_neighbors(pickup, drivers, k=2)

    assert [candidate.driver_id for candidate in result] == [2, 1]
    assert result[0].distance_km < result[1].distance_km


def test_nearest_neighbors_empty() -> None:
    assert nearest_neighbors(GeoPoint(0, 0), [], k=3) == []
