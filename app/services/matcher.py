from __future__ import annotations

import heapq
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from app.models import Driver
from app.services.geo import haversine_km


@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lng: float


@dataclass(frozen=True)
class MatchCandidate:
    distance_km: float
    driver_id: int


def nearest_neighbors(
    origin: GeoPoint,
    drivers: Iterable[Driver],
    k: int = 1,
) -> list[MatchCandidate]:
    """Return the k nearest drivers using a min-heap of Haversine distances."""
    if k < 1:
        raise ValueError("k must be >= 1")

    heap: list[tuple[float, int]] = []
    for driver in drivers:
        distance = haversine_km(origin.lat, origin.lng, driver.lat, driver.lng)
        heapq.heappush(heap, (distance, driver.id))

    winners: list[MatchCandidate] = []
    for _ in range(min(k, len(heap))):
        distance, driver_id = heapq.heappop(heap)
        winners.append(MatchCandidate(distance_km=round(distance, 4), driver_id=driver_id))
    return winners


def available_drivers(drivers: Sequence[Driver]) -> list[Driver]:
    return [driver for driver in drivers if driver.status == "available"]
