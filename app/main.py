from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.routers import dispatch, drivers, orders


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Delivery Matching and Dispatch Service",
    description="Match delivery orders to the nearest available driver using Haversine distance and a min-heap.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(drivers.router)
app.include_router(orders.router)
app.include_router(dispatch.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
