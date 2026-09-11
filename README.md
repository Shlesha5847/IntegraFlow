# IntegraFlow

A workflow orchestration engine that automates employee onboarding and offboarding across distributed REST APIs and legacy SOAP services with transactional state tracking and audit logging.

---

## Architecture

```
                          ┌───────────────────────────┐
                          │ React UI (localhost:5173) │
                          └─────────────┬─────────────┘
                                        │ HTTP / JSON
                                        ▼
                   ┌────────────────────────────────────────┐
                   │    FastAPI Backend (localhost:8080)    │
                   │    - Sequential Workflow Engine        │
                   │    - Employee Management Service       │
                   │    - PostgreSQL Audit Logger           │
                   └───────┬─────────────┬────────────┬─────┘
                           │             │            │
            ┌──────────────┘             │            └──────────────┐
            │ REST (HTTPX)               │ REST (HTTPX)              │ SOAP (Zeep)
            ▼                            ▼                           ▼
┌──────────────────────┐    ┌────────────────────────┐    ┌─────────────────────────┐
│ Identity Mock (8082) │    │ Ticketing Mock (8083)  │    │ Spyne SOAP Mock (8081)  │
│ - Provision Account  │    │ - Create IT Tickets    │    │ - Dynamic WSDL Contract │
│ - Revoke Account     │    │ - Close IT Tickets     │    │ - Update HRIS Record    │
└──────────────────────┘    └────────────────────────┘    └─────────────────────────┘
            │                            │                           │
            └────────────────────────────┼───────────────────────────┘
                                         ▼
                            ┌────────────────────────┐
                            │ PostgreSQL 16 (5432)   │
                            │ - employee             │
                            │ - workflow_run         │
                            │ - workflow_step        │
                            │ - audit_log            │
                            └────────────────────────┘
```

---

## Key Highlights

- **Multi-Protocol Integration:** Connects modern REST endpoints (Identity, Ticketing) and legacy SOAP/WSDL XML services (HRIS) within a unified pipeline.
- **Deterministic State Engine:** Executes steps sequentially (`PENDING` $\rightarrow$ `SUCCESS` / `FAILED`) and tracks lifecycle transitions in PostgreSQL.
- **Fail-Safe Halting:** Halts execution immediately if an intermediate step fails, marking the workflow as `FAILED_NEEDS_MANUAL_REVIEW` to prevent corrupted state.
- **Immutable Audit Trail:** Logs every execution event, timestamp, and vendor transaction ID (`IDN-*`, `TCK-*`, `SOAP-*`) for compliance tracking.
- **Decoupled Architecture:** Core engine communicates through abstract step interfaces and vendor adapters, isolating downstream protocol changes.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Integrations** | Zeep (SOAP Client), Spyne (SOAP Server / WSDL), HTTPX (REST Client) |
| **Database** | PostgreSQL 16 |
| **Frontend** | React 18, Vite |
| **Testing** | Pytest, unittest.mock, FastAPI TestClient |
| **Infrastructure** | Docker, Docker Compose |

---

## Running Locally

### 1. Start Services
```bash
docker compose up -d
```
Starts PostgreSQL (`5432`), Backend (`8080`), Identity (`8082`), Ticketing (`8083`), and Legacy HR SOAP (`8081`).

### 2. Run Tests
```bash
docker run --rm -v "${PWD}/backend:/app" -w /app python:3.11-slim sh -c "pip install --no-cache-dir -r requirements.txt > /dev/null && pytest -v"
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
UI runs on `http://localhost:5173`.

---

## Design Decisions

- **Sequential Execution over Queues:** Kept orchestration synchronous and deterministic to simplify state tracking and failure debugging for fixed 3-step pipelines.
- **Adapter Pattern:** Isolated network and protocol specifics within dedicated adapter classes, allowing live vendor swaps without modifying workflow engine logic.
- **Halt-on-Failure:** Prioritized explicit manual review states over automated retries to avoid duplicating side effects in downstream vendor systems.
