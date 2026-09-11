from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.enums import WorkflowType, WorkflowStatus, StepStatus, IntegrationType

class WorkflowStepResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: Optional[int] = None
    workflow_run_id: Optional[int] = None
    step_order: int
    step_name: str
    integration_type: IntegrationType
    status: StepStatus
    error_message: Optional[str] = None
    executed_at: Optional[datetime] = None

class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: int
    employee_id: int
    workflow_type: WorkflowType
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[WorkflowStepResponse] = []

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: int
    workflow_run_id: int
    event: str
    detail: Optional[str] = None
    created_at: datetime

class VendorResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
