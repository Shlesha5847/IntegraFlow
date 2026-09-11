from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging

from app.models.employee import Employee
from app.models.workflow_run import WorkflowRun
from app.models.workflow_step import WorkflowStep
from app.models.enums import EmployeeStatus, WorkflowType, WorkflowStatus, StepStatus, IntegrationType
from app.engine.base import WorkflowStepDefinition
from app.engine.identity_step import IdentityStepExecutor
from app.engine.ticketing_step import TicketingStepExecutor
from app.engine.legacy_hr_soap_step import LegacyHrSoapStepExecutor
from app.services.audit_service import AuditService
from app.adapters.exceptions import ResourceNotFoundException

logger = logging.getLogger("WorkflowEngineService")

class WorkflowEngineService:
    def __init__(
        self,
        audit_service: AuditService = None,
        identity_step_executor: IdentityStepExecutor = None,
        ticketing_step_executor: TicketingStepExecutor = None,
        legacy_hr_soap_step_executor: LegacyHrSoapStepExecutor = None
    ):
        self.audit_service = audit_service or AuditService()
        self.identity_step_executor = identity_step_executor or IdentityStepExecutor()
        self.ticketing_step_executor = ticketing_step_executor or TicketingStepExecutor()
        self.legacy_hr_soap_step_executor = legacy_hr_soap_step_executor or LegacyHrSoapStepExecutor()

    def start_onboarding(self, db: Session, employee_id: int) -> WorkflowRun:
        employee = self._get_employee_or_throw(db, employee_id)
        step_definitions = [
            WorkflowStepDefinition(1, "CREATE_IDENTITY", IntegrationType.REST, self.identity_step_executor),
            WorkflowStepDefinition(2, "CREATE_IT_TICKETS", IntegrationType.REST, self.ticketing_step_executor),
            WorkflowStepDefinition(3, "UPDATE_HR_RECORD_SOAP", IntegrationType.SOAP, self.legacy_hr_soap_step_executor)
        ]
        return self._execute_workflow(db, employee, WorkflowType.ONBOARDING, step_definitions)

    def start_offboarding(self, db: Session, employee_id: int) -> WorkflowRun:
        employee = self._get_employee_or_throw(db, employee_id)
        step_definitions = [
            WorkflowStepDefinition(1, "DEACTIVATE_IDENTITY", IntegrationType.REST, self.identity_step_executor),
            WorkflowStepDefinition(2, "CLOSE_IT_TICKETS", IntegrationType.REST, self.ticketing_step_executor),
            WorkflowStepDefinition(3, "UPDATE_HR_RECORD_SOAP", IntegrationType.SOAP, self.legacy_hr_soap_step_executor)
        ]
        return self._execute_workflow(db, employee, WorkflowType.OFFBOARDING, step_definitions)

    def get_workflow_run_by_id(self, db: Session, run_id: int) -> WorkflowRun:
        run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
        if not run:
            raise ResourceNotFoundException(f"Workflow run not found with id: {run_id}")
        return run

    def get_workflow_runs_by_employee_id(self, db: Session, employee_id: int) -> List[WorkflowRun]:
        self._get_employee_or_throw(db, employee_id)
        return db.query(WorkflowRun).filter(WorkflowRun.employee_id == employee_id).order_by(WorkflowRun.started_at.desc()).all()

    def _execute_workflow(self, db: Session, employee: Employee, workflow_type: WorkflowType, step_definitions: List[WorkflowStepDefinition]) -> WorkflowRun:
        logger.info(f"Starting {workflow_type} workflow for employee #{employee.id}: {employee.full_name} ({employee.email})")

        run = WorkflowRun(
            employee_id=employee.id,
            workflow_type=workflow_type,
            status=WorkflowStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        run.employee = employee
        db.add(run)
        db.commit()
        db.refresh(run)

        self.audit_service.log_event(
            db, run, "WORKFLOW_STARTED",
            f"Started {workflow_type} workflow for employee {employee.full_name} ({employee.email})"
        )

        any_step_failed = False

        for step_def in step_definitions:
            step = WorkflowStep(
                workflow_run_id=run.id,
                step_order=step_def.step_order,
                step_name=step_def.step_name,
                integration_type=step_def.integration_type,
                status=StepStatus.PENDING
            )
            db.add(step)
            db.commit()
            db.refresh(step)

            logger.info(f"Executing step #{step_def.step_order}: {step_def.step_name} ({step_def.integration_type})")
            result = step_def.step_executor.execute(run, step)

            if result.success:
                step.status = StepStatus.SUCCESS
                step.executed_at = datetime.utcnow()
                db.commit()
                db.refresh(step)

                self.audit_service.log_event(
                    db, run, "STEP_SUCCESS",
                    f"Step {step_def.step_order} [{step_def.step_name}] succeeded: {result.message}"
                )
            else:
                step.status = StepStatus.FAILED
                step.error_message = result.error_message
                step.executed_at = datetime.utcnow()
                db.commit()
                db.refresh(step)

                self.audit_service.log_event(
                    db, run, "STEP_FAILED",
                    f"Step {step_def.step_order} [{step_def.step_name}] failed: {result.error_message}"
                )

                any_step_failed = True
                break  # Stop sequential execution immediately on failure

        if any_step_failed:
            run.status = WorkflowStatus.FAILED_NEEDS_MANUAL_REVIEW
            run.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(run)

            self.audit_service.log_event(
                db, run, "WORKFLOW_FAILED",
                f"{workflow_type} workflow halted due to failure. Marked as FAILED_NEEDS_MANUAL_REVIEW."
            )
        else:
            run.status = WorkflowStatus.COMPLETED
            run.completed_at = datetime.utcnow()

            if workflow_type == WorkflowType.ONBOARDING:
                employee.status = EmployeeStatus.ACTIVE
            elif workflow_type == WorkflowType.OFFBOARDING:
                employee.status = EmployeeStatus.INACTIVE

            db.commit()
            db.refresh(run)

            self.audit_service.log_event(
                db, run, "WORKFLOW_COMPLETED",
                f"{workflow_type} workflow completed successfully. Employee status updated to {employee.status}."
            )

        return run

    def _get_employee_or_throw(self, db: Session, employee_id: int) -> Employee:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise ResourceNotFoundException(f"Employee not found with id: {employee_id}")
        return emp
