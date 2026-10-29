from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Assignment, AssignmentStatus, Driver, DriverStatus, Order, OrderStatus
from app.services.matcher import GeoPoint, MatchCandidate, available_drivers, nearest_neighbors


def list_available_drivers(db: Session) -> list[Driver]:
    return list(db.scalars(select(Driver).where(Driver.status == DriverStatus.AVAILABLE.value)))


def preview_matches(
    db: Session,
    pickup_lat: float,
    pickup_lng: float,
    k: int | None = None,
) -> list[MatchCandidate]:
    drivers = available_drivers(list_available_drivers(db))
    return nearest_neighbors(GeoPoint(pickup_lat, pickup_lng), drivers, k=k or settings.match_k)


def dispatch_order(db: Session, order: Order, k: int | None = None) -> Assignment:
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"order {order.id} is {order.status}, not pending",
        )

    candidates = preview_matches(db, order.pickup_lat, order.pickup_lng, k=k or 1)
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="no available drivers near pickup",
        )

    best = candidates[0]
    driver = db.get(Driver, best.driver_id)
    if driver is None or driver.status != DriverStatus.AVAILABLE.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="matched driver is no longer available",
        )

    assignment = Assignment(
        order_id=order.id,
        driver_id=driver.id,
        distance_km=best.distance_km,
        status=AssignmentStatus.ACTIVE.value,
    )
    order.status = OrderStatus.DISPATCHED.value
    driver.status = DriverStatus.BUSY.value
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    db.refresh(order)
    db.refresh(driver)
    return assignment
