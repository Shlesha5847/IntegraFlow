from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.workflow import WorkflowRunResponse, AuditLogResponse
from app.services.workflow_engine_service import WorkflowEngineService
from app.services.audit_service import AuditService

router = APIRouter(prefix="", tags=["Workflows"])
workflow_service = WorkflowEngineService()
audit_service = AuditService()

@router.post("/workflows/onboard/{employee_id}", response_model=WorkflowRunResponse, status_code=status.HTTP_200_OK)
@router.post("/api/workflows/onboard/{employee_id}", response_model=WorkflowRunResponse, include_in_schema=False)
def start_onboarding(employee_id: int, db: Session = Depends(get_db)):
    return workflow_service.start_onboarding(db, employee_id)

@router.post("/workflows/offboard/{employee_id}", response_model=WorkflowRunResponse, status_code=status.HTTP_200_OK)
@router.post("/api/workflows/offboard/{employee_id}", response_model=WorkflowRunResponse, include_in_schema=False)
def start_offboarding(employee_id: int, db: Session = Depends(get_db)):
    return workflow_service.start_offboarding(db, employee_id)

@router.get("/workflows/{run_id}", response_model=WorkflowRunResponse)
@router.get("/api/workflows/{run_id}", response_model=WorkflowRunResponse, include_in_schema=False)
def get_workflow_run(run_id: int, db: Session = Depends(get_db)):
    return workflow_service.get_workflow_run_by_id(db, run_id)

@router.get("/workflows/{run_id}/audit", response_model=List[AuditLogResponse])
@router.get("/api/workflows/{run_id}/audit", response_model=List[AuditLogResponse], include_in_schema=False)
def get_workflow_audit_logs(run_id: int, db: Session = Depends(get_db)):
    return audit_service.get_audit_logs_for_run(db, run_id)

@router.get("/workflows/employee/{employee_id}", response_model=List[WorkflowRunResponse])
@router.get("/api/workflows/employee/{employee_id}", response_model=List[WorkflowRunResponse], include_in_schema=False)
def get_employee_workflow_runs(employee_id: int, db: Session = Depends(get_db)):
    return workflow_service.get_workflow_runs_by_employee_id(db, employee_id)
