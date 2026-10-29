from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Assignment, AssignmentStatus, Driver, DriverStatus, Order, OrderStatus
from app.schemas import (
    AssignmentRead,
    DispatchResponse,
    DriverRead,
    MatchCandidateRead,
    MatchPreviewResponse,
    OrderRead,
)
from app.services.dispatcher import dispatch_order, preview_matches

router = APIRouter(tags=["dispatch"])


@router.get("/dispatch/match", response_model=MatchPreviewResponse)
def match_preview(
    pickup_lat: float = Query(ge=-90, le=90),
    pickup_lng: float = Query(ge=-180, le=180),
    k: int = Query(default=None, ge=1, le=50),
    db: Session = Depends(get_db),
) -> MatchPreviewResponse:
    candidates = preview_matches(db, pickup_lat, pickup_lng, k=k or settings.match_k)
    enriched: list[MatchCandidateRead] = []
    for candidate in candidates:
        driver = db.get(Driver, candidate.driver_id)
        enriched.append(
            MatchCandidateRead(
                driver_id=candidate.driver_id,
                distance_km=candidate.distance_km,
                driver=DriverRead.model_validate(driver) if driver else None,
            )
        )
    return MatchPreviewResponse(
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        candidates=enriched,
    )


@router.post("/orders/{order_id}/dispatch", response_model=DispatchResponse)
def dispatch_existing_order(order_id: int, db: Session = Depends(get_db)) -> DispatchResponse:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    assignment = dispatch_order(db, order)
    driver = db.get(Driver, assignment.driver_id)
    return DispatchResponse(
        assignment=AssignmentRead.model_validate(assignment),
        order=OrderRead.model_validate(order),
        driver=DriverRead.model_validate(driver),
    )


@router.post("/assignments/{assignment_id}/complete", response_model=AssignmentRead)
def complete_assignment(assignment_id: int, db: Session = Depends(get_db)) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assignment not found")
    if assignment.status != AssignmentStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"assignment is {assignment.status}",
        )

    assignment.status = AssignmentStatus.COMPLETED.value
    order = db.get(Order, assignment.order_id)
    driver = db.get(Driver, assignment.driver_id)
    if order is not None:
        order.status = OrderStatus.COMPLETED.value
    if driver is not None:
        driver.status = DriverStatus.AVAILABLE.value
    db.commit()
    db.refresh(assignment)
    return assignment
