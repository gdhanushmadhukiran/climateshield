# ClimateShield — FastAPI + PostgreSQL/PostGIS Backend Foundation

Production-grade operational intelligence API backend foundation for ClimateShield, designed for resilient climate data ingestion, risk analysis, infrastructure asset monitoring, and decision support.

---

## 1. Tech Stack

- **Framework**: FastAPI (Python 3.12 - 3.14 compatible)
- **Validation**: Pydantic v2 with strict schemas
- **ORM**: SQLAlchemy 2.0 (declarative 2.x patterns)
- **Spatial Engine**: PostGIS 3.4 / GeoAlchemy2 / Shapely (EPSG:4326 GeoJSON)
- **Migrations**: Alembic
- **Testing**: pytest, HTTPX TestClient
- **Database**: PostgreSQL 16 + PostGIS (with local SQLite dev/test fallback)

---

## 2. Quick Start & Project Commands

### Installation

```bash
cd backend
python -m pip install -r requirements.txt
```

### Environment Configuration

```bash
cp .env.example .env
```

### Run Migrations

```bash
python -m alembic upgrade head
```

### Seed Development Database (Visakhapatnam Dataset)

```bash
python -m app.seed.demo_seed
```

### Start Development Server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive documentation:

- OpenAPI / Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/api/v1/openapi.json`

### Run Automated Tests

```bash
python -m pytest tests/ -v
```

### Docker Deployment (PostgreSQL + PostGIS + FastAPI)

```bash
docker compose up --build -d
```

---

## 3. Endpoints & API Contract

| Endpoint                               | Method | Description                                                                 |
| :------------------------------------- | :----: | :-------------------------------------------------------------------------- |
| `/health`                              |  GET   | Root liveness check (no DB dependency)                                      |
| `/api/v1/system/health`                |  GET   | Deep subsystem health check verifying DB connectivity                       |
| `/api/v1/city`                         |  GET   | Primary city profile (Visakhapatnam)                                        |
| `/api/v1/risk/current`                 |  GET   | Real-time aggregate city risk score & metadata                              |
| `/api/v1/risk/zones`                   |  GET   | Risk zones list with EPSG:4326 GeoJSON polygons & drivers                   |
| `/api/v1/risk/zones/{id}`              |  GET   | Specific risk zone telemetry & drivers                                      |
| `/api/v1/assets`                       |  GET   | Critical infrastructure assets (Hospitals, Substations, etc.)               |
| `/api/v1/incidents`                    |  GET   | Active climate incidents                                                    |
| `/api/v1/incidents/{id}/status`        |  POST  | Update incident response status (`ACKNOWLEDGED`, `IN_RESPONSE`, `RESOLVED`) |
| `/api/v1/alerts`                       |  GET   | Active alert notifications                                                  |
| `/api/v1/alerts/{id}/acknowledge`      |  POST  | Operator alert acknowledgement                                              |
| `/api/v1/river/nodes`                  |  GET   | Upstream → Midstream → Downstream sensor topology                           |
| `/api/v1/data-sources`                 |  GET   | Connected telemetry data sources                                            |
| `/api/v1/forecast/trajectory`          |  GET   | 12-hour probabilistic forecast trajectory                                   |
| `/api/v1/cascade/graph`                |  GET   | Systemic failure cascade network graph                                      |
| `/api/v1/optimization/recommendations` |  GET   | Action recommendations for operators                                        |
