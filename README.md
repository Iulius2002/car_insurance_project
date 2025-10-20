# 🚗 Car Insurance API

A FastAPI service to manage **owners**, **cars**, **insurance policies**, and **claims**.  
It provides clean REST endpoints, strict validation, background policy-expiry logging, and full persistence with SQLAlchemy + Alembic.

> **Quick links**
>
> - Local dev: `uvicorn app.main:app --reload --port 8001`
> - Docker (Rancher Desktop): `nerdctl compose up -d --build`
> - API docs: `http://localhost:8001/docs`  
> - Health: `GET /health`

---

## ✨ Features

- Owners ↔ Cars (1:N)
- Policies with **inclusive** validity (active if `start_date ≤ d ≤ end_date`)
- **Single active policy per car** enforced in code + **Postgres GiST exclusion constraint**
- Claims with positive amounts and server-side `created_at`
- **History** endpoint (policies + claims ordered chronologically)
- **APScheduler** job that logs policy expirations once within 1h window
- **Pydantic v2** models with strict validation
- **Alembic** migrations (baseline → constraints → indexes)
- **Structured logging** with `structlog` + **X-Request-ID** middleware

---

## 🧰 Tech Stack

- **Runtime**: Python 3.11+, ASGI
- **Web/API**: FastAPI
- **ORM**: SQLAlchemy 2.x
- **Schema/Validation**: Pydantic v2
- **Migrations**: Alembic
- **Database**: SQLite (local), PostgreSQL (Docker/Rancher)
- **Background jobs**: APScheduler
- **Logging**: structlog

---

## 📁 Project Structure

app/
main.py
api/
routers/
cars.py
claims.py
policies.py
history.py
health.py
deps.py
errors.py
schemas.py
middleware.py # Request-ID middleware
core/
config.py # pydantic-settings
logging.py
scheduling.py # APScheduler + job
context.py # request_id context var
db/
base.py
session.py
models.py
repositories.py
services/
policy_service.py
claim_service.py
history_service.py
validity_service.py
utils/
dates.py
alembic/
versions/ # migration scripts
scripts/
seed_demo.py # demo seeds (cars/owners + sample policies/claims)
tests/
api/
services/
utils/

pgsql
Copy code

---

## ⚙️ Configuration

Environment variables (via **.env** or container env):

| Key                 | Example                                                  | Notes |
|---------------------|----------------------------------------------------------|------|
| `DATABASE_URL`      | `sqlite:///./carins.db` or `postgresql+psycopg://…`      | SQLAlchemy URL |
| `LOG_LEVEL`         | `DEBUG`                                                  | default INFO |
| `SCHEDULER_ENABLED` | `true` / `false`                                         | enable APScheduler |
| `SCHEDULER_TEST_MODE` | `true`                                                | easier local testing |

**.env example (local dev, SQLite):**
```dotenv
DATABASE_URL=sqlite:///./carins.db
LOG_LEVEL=DEBUG
SCHEDULER_ENABLED=true
SCHEDULER_TEST_MODE=true
.env.docker (Docker, Postgres):

dotenv
Copy code
DATABASE_URL=postgresql+psycopg://carins:carins@db:5432/carins
LOG_LEVEL=DEBUG
SCHEDULER_ENABLED=true
SCHEDULER_TEST_MODE=true
▶️ Running Locally (no Docker)
bash
Copy code
# 1) Create venv & install deps
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2) Create .env (see examples above)

# 3) Initialize DB
alembic upgrade head

# 4) (Optional) seed demo data
python -m scripts.seed_demo

# 5) Start the API
uvicorn app.main:app --reload --port 8001

# 6) Open docs
# http://localhost:8001/docs
🐳 Run with Docker (Rancher Desktop)
Works with Rancher containerd using nerdctl compose.
The compose maps DB to host 5433 to avoid local conflicts and API to 8001.

docker-compose.yml

yaml
Copy code
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: carins
      POSTGRES_PASSWORD: carins
      POSTGRES_DB: carins
    ports:
      - "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build: .
    environment:
      - DATABASE_URL=postgresql+psycopg://carins:carins@db:5432/carins
      - LOG_LEVEL=DEBUG
      - SCHEDULER_ENABLED=true
      - SCHEDULER_TEST_MODE=true
    depends_on:
      - db
    ports:
      - "8001:8000"
    restart: unless-stopped

volumes:
  pgdata: {}
Dockerfile

dockerfile
Copy code
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

# normalize CRLF on Windows clones and ensure exec bit
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
entrypoint.sh

sh
Copy code
#!/bin/sh
set -eu

# wait for DB to accept connections
python - <<'PY'
import os, time, sys
import psycopg
url = os.environ["DATABASE_URL"].replace("+psycopg","")
for _ in range(60):
    try:
        with psycopg.connect(url, connect_timeout=3):
            sys.exit(0)
    except Exception:
        time.sleep(1)
print("DB not ready after 60s", file=sys.stderr); sys.exit(1)
PY

echo "Running alembic migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
Build & Run

powershell
Copy code
# Rancher Desktop (containerd):
nerdctl compose up -d --build
nerdctl compose ps
nerdctl compose logs -f

# Seed demo data
nerdctl compose exec api python -m scripts.seed_demo

# Health
Invoke-RestMethod http://localhost:8001/health
Windows note: prefer http://localhost:8001 over http://127.0.0.1:8001 if you see timeouts (proxy/VPN quirk).

🧪 Tests
bash
Copy code
pytest -q
# or inside the container
nerdctl compose exec api pytest -q
Coverage target: ≥ 80% (services + API validation + scheduler logic).

🔌 Endpoints (Quick Reference)
Health

GET /health → {"status":"ok"}

Cars

GET /api/cars → list of cars with owner

json
Copy code
[
  {
    "id": 1,
    "vin": "WVWZZZ1JZXW000001",
    "make": "VW",
    "model": "Golf",
    "yearOfManufacture": 2018,
    "owner": { "id": 1, "name": "Alice", "email": "a@example.com" }
  }
]
Policies

POST /api/cars/{carId}/policies

json
Copy code
{ "provider": "AXA", "startDate": "2025-01-01", "endDate": "2025-06-30" }
Validates: endDate ≥ startDate, no overlap with existing policies.
400 if overlap; 404 if car not found.

Insurance validity

GET /api/cars/{carId}/insurance-valid?date=YYYY-MM-DD

json
Copy code
{ "carId": 1, "date": "2025-03-01", "valid": true }
Claims

POST /api/cars/{carId}/claims

json
Copy code
{ "claimDate": "2025-03-05", "description": "Rear bumper", "amount": 450.00 }
Validates: positive amount, non-empty description, real ISO date.

History

GET /api/cars/{carId}/history (ascending)

json
Copy code
[
  { "type": "POLICY", "policyId": 2, "startDate": "2025-01-02", "endDate": "2026-01-01", "provider": "Allianz" },
  { "type": "CLAIM",  "claimId": 2, "claimDate": "2025-03-05", "amount": 450.00, "description": "Rear bumper" }
]
🗄️ Database Schema (Key Tables)
owner: id, name (NOT NULL), email (nullable)

car: id, vin (UNIQUE, NOT NULL), make, model, year_of_manufacture, owner_id (FK NOT NULL)

insurance_policy: id, car_id (FK), provider, start_date (DATE NOT NULL), end_date (DATE NOT NULL)

Constraint: Postgres EXCLUDE USING gist on (car_id WITH =, daterange(start_date, end_date, '[]') WITH &&) to prevent overlaps

claim: id, car_id (FK), claim_date (DATE NOT NULL), description (NOT NULL), amount (DECIMAL(12,2) > 0), created_at (TIMESTAMP DEFAULT NOW())

Indexes

car(vin) unique

insurance_policy(car_id, start_date, end_date)

claim(car_id, claim_date)

🕒 Scheduler (Policy Expiry Logger)
Runs every 10 minutes (configurable)

For policies with end_date == today (server local date), logs once:

pgsql
Copy code
Policy {id} for car {carId} expired on {endDate}
Idempotent via “logged once” mechanism (field or log table; implemented in service/job)

🧾 Logging & Request Tracing
JSON logs via structlog (timestamp, level, message, request_id, …)

Request-ID middleware:

Reads X-Request-ID header or generates one

Echoes it back in response headers

Injects into all logs via context var

Example:

json
Copy code
{"timestamp":"2025-10-20T12:14:58.801406Z","level":"info","message":"scheduler_started","request_id":"demo-123","job_id":"policy-expiry-logger"}
🧪 Seeding
bash
Copy code
# local
python -m scripts.seed_demo

# docker
nerdctl compose exec api python -m scripts.seed_demo
If re-seeding, either make the script idempotent or reset data:

bash
Copy code
# destructive: removes all data
nerdctl compose exec db psql -U carins -d carins -c "TRUNCATE TABLE claim, insurance_policy, car, owner RESTART IDENTITY CASCADE;"
🧯 Troubleshooting
/api/cars hangs but /health works
Use http://localhost:8001 instead of 127.0.0.1 on some Windows setups (proxy/VPN quirk).
Or set NO_PROXY=localhost,127.0.0.1.

Docker “exec format error” for /app/entrypoint.sh
Ensure LF endings and chmod +x (Dockerfile step already fixes with sed -i 's/\r$//' + chmod).

Port conflicts
Change host mapping in compose: DB 5433:5432, API 8001:8000.

Alembic migration fails with policy overlap
Clean up overlapping rows or truncate tables, then re-run alembic upgrade head.

Rebuild after changes

bash
Copy code
nerdctl compose build --no-cache api
nerdctl compose up -d api
🔒 Data Integrity & Validation Summary
Dates: ISO YYYY-MM-DD, realistic range (1900–2100)

Claims: amount > 0

Policies: end_date ≥ start_date; no overlaps per car

404 when referencing missing car

Clear 400/422 messages on validation failures
