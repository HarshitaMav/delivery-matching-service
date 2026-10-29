# Delivery Matching and Dispatch Service

FastAPI service that assigns delivery orders to the nearest available driver.

Matching uses **Haversine distance** and a **min-heap** (`heapq`) nearest-neighbor search over currently available drivers.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness check |
| `POST` | `/drivers` | Register a driver (lat/lng + status) |
| `GET` | `/drivers` | List drivers |
| `PATCH` | `/drivers/{id}/location` | Update live GPS |
| `PATCH` | `/drivers/{id}/status` | `available` / `busy` / `offline` |
| `POST` | `/orders` | Create an order (`auto_dispatch: true` to assign immediately) |
| `POST` | `/orders/{id}/dispatch` | Match and assign the nearest available driver |
| `GET` | `/dispatch/match` | Preview k nearest drivers without assigning |
| `POST` | `/assignments/{id}/complete` | Finish a delivery and free the driver |

Interactive docs: `http://localhost:8000/docs`

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

SQLite is the default (`./dispatch.db`). Copy `.env.example` to `.env` to override `DATABASE_URL`.

## Tests

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Compose starts PostgreSQL and the API on port `8000`.
