from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Driver, Order
from app.schemas import DispatchResponse, DriverRead, OrderCreate, OrderRead
from app.services.dispatcher import dispatch_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead | DispatchResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    auto_dispatch = data.pop("auto_dispatch")
    order = Order(**data)
    db.add(order)
    db.commit()
    db.refresh(order)

    if not auto_dispatch:
        return order

    assignment = dispatch_order(db, order)
    driver = db.get(Driver, assignment.driver_id)
    return DispatchResponse(
        assignment=assignment,
        order=order,
        driver=DriverRead.model_validate(driver),
    )


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)) -> list[Order]:
    return list(db.scalars(select(Order).order_by(Order.id)))


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return order
