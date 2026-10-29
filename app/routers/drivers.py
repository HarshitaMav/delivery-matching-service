from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Driver
from app.schemas import DriverCreate, DriverLocationUpdate, DriverRead, DriverStatusUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)) -> Driver:
    driver = Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("", response_model=list[DriverRead])
def list_drivers(db: Session = Depends(get_db)) -> list[Driver]:
    return list(db.scalars(select(Driver).order_by(Driver.id)))


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, db: Session = Depends(get_db)) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="driver not found")
    return driver


@router.patch("/{driver_id}/location", response_model=DriverRead)
def update_location(
    driver_id: int, payload: DriverLocationUpdate, db: Session = Depends(get_db)
) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="driver not found")
    driver.lat = payload.lat
    driver.lng = payload.lng
    db.commit()
    db.refresh(driver)
    return driver


@router.patch("/{driver_id}/status", response_model=DriverRead)
def update_status(
    driver_id: int, payload: DriverStatusUpdate, db: Session = Depends(get_db)
) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="driver not found")
    driver.status = payload.status
    db.commit()
    db.refresh(driver)
    return driver
