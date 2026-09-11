from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import engine, Base
from app.routers import employees, workflows
from app.adapters.exceptions import ResourceNotFoundException, DuplicateResourceException, VendorIntegrationException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("integraflow-backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down IntegraFlow backend.")

app = FastAPI(
    title="IntegraFlow API",
    description="Employee Onboarding/Offboarding Multi-Protocol Automation Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": 404, "error": "Not Found", "message": str(exc), "path": request.url.path}
    )

@app.exception_handler(DuplicateResourceException)
async def duplicate_resource_handler(request: Request, exc: DuplicateResourceException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"status": 409, "error": "Conflict", "message": str(exc), "path": request.url.path}
    )

@app.exception_handler(VendorIntegrationException)
async def vendor_integration_handler(request: Request, exc: VendorIntegrationException):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"status": 502, "error": "Bad Gateway", "message": str(exc), "path": request.url.path}
    )

app.include_router(employees.router)
app.include_router(workflows.router)

@app.get("/health")
def health():
    return {"status": "UP", "service": "integraflow-backend"}
