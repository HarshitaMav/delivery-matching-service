from fastapi.testclient import TestClient


def _driver(client: TestClient, name: str, lat: float, lng: float, status: str = "available"):
    response = client.post(
        "/drivers",
        json={"name": name, "lat": lat, "lng": lng, "status": status, "vehicle_type": "bike"},
    )
    assert response.status_code == 201
    return response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dispatch_assigns_nearest_available_driver(client: TestClient) -> None:
    near = _driver(client, "Asha", 40.7589, -73.9851)
    _driver(client, "Ben", 40.6782, -73.9442)
    _driver(client, "Cara", 40.7306, -73.9352, status="offline")

    order = client.post(
        "/orders",
        json={
            "customer_name": "Priya",
            "pickup_lat": 40.7580,
            "pickup_lng": -73.9855,
            "dropoff_lat": 40.7484,
            "dropoff_lng": -73.9857,
        },
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    dispatched = client.post(f"/orders/{order_id}/dispatch")
    assert dispatched.status_code == 200
    body = dispatched.json()
    assert body["driver"]["id"] == near["id"]
    assert body["order"]["status"] == "dispatched"
    assert body["driver"]["status"] == "busy"
    assert body["assignment"]["distance_km"] >= 0


def test_auto_dispatch_and_complete(client: TestClient) -> None:
    driver = _driver(client, "Dee", 37.7749, -122.4194)
    created = client.post(
        "/orders",
        json={
            "customer_name": "Sam",
            "pickup_lat": 37.7750,
            "pickup_lng": -122.4195,
            "dropoff_lat": 37.7840,
            "dropoff_lng": -122.4090,
            "auto_dispatch": True,
        },
    )
    assert created.status_code == 201
    assignment_id = created.json()["assignment"]["id"]

    done = client.post(f"/assignments/{assignment_id}/complete")
    assert done.status_code == 200
    assert done.json()["status"] == "completed"

    refreshed = client.get(f"/drivers/{driver['id']}")
    assert refreshed.json()["status"] == "available"


def test_dispatch_fails_without_available_drivers(client: TestClient) -> None:
    _driver(client, "Eve", 40.7, -74.0, status="busy")
    order = client.post(
        "/orders",
        json={
            "customer_name": "No Driver",
            "pickup_lat": 40.71,
            "pickup_lng": -74.01,
            "dropoff_lat": 40.72,
            "dropoff_lng": -74.02,
        },
    )
    dispatched = client.post(f"/orders/{order.json()['id']}/dispatch")
    assert dispatched.status_code == 409


def test_match_preview_ranks_drivers(client: TestClient) -> None:
    closer = _driver(client, "Near", 40.7589, -73.9851)
    farther = _driver(client, "Far", 40.6782, -73.9442)
    preview = client.get(
        "/dispatch/match",
        params={"pickup_lat": 40.7580, "pickup_lng": -73.9855, "k": 2},
    )
    assert preview.status_code == 200
    ids = [c["driver_id"] for c in preview.json()["candidates"]]
    assert ids == [closer["id"], farther["id"]]
