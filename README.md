# IntegraFlow

##  One-Line Summary
A multi-protocol workflow orchestration engine that automates employee onboarding/offboarding by coordinating distributed REST and legacy SOAP vendor systems with transactional state tracking and audit logging.

---

##  Architecture

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

##  Key Features

- **Multi-Protocol Orchestration:** Coordinates modern REST/JSON microservices and legacy SOAP 1.1/XML endpoints within a unified execution pipeline.
- **Sequential Step Engine:** Enforces ordered execution (`Identity` $\rightarrow$ `Ticketing` $\rightarrow$ `Legacy HR`) with deterministic state progression (`PENDING` $\rightarrow$ `SUCCESS` / `FAILED`).
- **Fail-Safe Circuitry:** Automatically halts downstream execution upon intermediate step failure, transitioning the workflow to `FAILED_NEEDS_MANUAL_REVIEW` to prevent state corruption.
- **Append-Only Audit Trail:** Persists immutable transaction logs, timestamps, and vendor IDs (`IDN-*`, `TCK-*`, `SOAP-*`) in PostgreSQL for enterprise compliance.
- **Live State Visibility:** Real-time frontend polling interface displaying step-by-step progress and execution health.

---

##  Why This Project Stands Out

> Most student projects are basic CRUD applications that interact with a single database. **IntegraFlow solves a real-world enterprise integration problem.**

- **Multi-Protocol Integration (REST + SOAP):** Real enterprise environments are hybrid. IntegraFlow connects modern REST APIs with legacy SOAP/WSDL services using custom adapters and strict schema contracts.
- **Workflow State Machine (Not Just Endpoints):** Implements a resilient step-execution engine that manages state transitions, step dependencies, and lifecycle events across distributed boundaries.
- **Enterprise Fault Tolerance:** Prevents partial execution states by enforcing immediate halt-on-failure semantics rather than blindly proceeding with downstream side effects.
- **Clean Architecture & Separation of Concerns:** Core orchestration logic depends on abstract step interfaces and domain entities, completely decoupled from vendor transport layers.

---

##  Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Integrations:** Zeep (SOAP Client), Spyne (SOAP Server / WSDL), HTTPX (REST Client)
- **Database:** PostgreSQL 16
- **Frontend:** React 18, Vite
- **Testing:** Pytest, unittest.mock, FastAPI TestClient
- **Infrastructure:** Docker, Docker Compose

---

##  Running Locally

### 1. Start All Services (Database + Backend + 3 Mock Vendors)
```bash
docker compose up -d
```

### 2. Run Test Suite
```bash
docker run --rm -v "${PWD}/backend:/app" -w /app python:3.11-slim sh -c "pip install --no-cache-dir -r requirements.txt > /dev/null && pytest -v"
```

### 3. Launch Frontend UI
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:5173` (Backend at `http://localhost:8080`).

---

##  Testing

Includes a unit test suite built with **Pytest** and **FastAPI TestClient** covering workflow engine completion, halt-on-failure branching, step ordering, REST adapter error handling, and API status codes.

---

##  Design Decisions

- **Sequential Execution over Queues:** Prioritized deterministic execution, transparent state transitions, and straightforward debugging over the operational overhead of message brokers for small step pipelines.
- **Adapter Design Pattern:** Isolated third-party protocol logic inside `IdentityRestAdapter`, `TicketingRestAdapter`, and `LegacyHrSoapAdapter`, allowing live enterprise vendor swaps without touching the core engine.
- **Explicit Halt-on-Failure:** Chose fail-safe manual review transitions over blind auto-retries to avoid duplicate side effects in external vendor systems.

---

##  Out of Scope

- Distributed message streaming (Kafka / RabbitMQ)
- Production authentication / OAuth2 SSO
- Automated retry policies and distributed locking
