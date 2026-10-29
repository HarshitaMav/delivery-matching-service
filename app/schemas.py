from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DriverCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    vehicle_type: str = "car"
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    status: str = "available"


class DriverLocationUpdate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class DriverStatusUpdate(BaseModel):
    status: str = Field(pattern="^(available|busy|offline)$")


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    vehicle_type: str
    lat: float
    lng: float
    status: str
    updated_at: datetime | None = None


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    pickup_lat: float = Field(ge=-90, le=90)
    pickup_lng: float = Field(ge=-180, le=180)
    dropoff_lat: float = Field(ge=-90, le=90)
    dropoff_lng: float = Field(ge=-180, le=180)
    auto_dispatch: bool = False


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float
    status: str
    created_at: datetime | None = None


class MatchCandidateRead(BaseModel):
    driver_id: int
    distance_km: float
    driver: DriverRead | None = None


class MatchPreviewResponse(BaseModel):
    order_id: int | None = None
    pickup_lat: float
    pickup_lng: float
    candidates: list[MatchCandidateRead]


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    driver_id: int
    distance_km: float
    status: str
    assigned_at: datetime | None = None


class DispatchResponse(BaseModel):
    assignment: AssignmentRead
    order: OrderRead
    driver: DriverRead
