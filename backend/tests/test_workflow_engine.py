import pytest
from unittest.mock import MagicMock, call
from datetime import datetime

from app.models.employee import Employee
from app.models.workflow_run import WorkflowRun
from app.models.workflow_step import WorkflowStep
from app.models.enums import EmployeeStatus, WorkflowType, WorkflowStatus, StepStatus, IntegrationType
from app.engine.base import StepExecutionResult
from app.services.workflow_engine_service import WorkflowEngineService

@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mock add, commit, refresh
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db

@pytest.fixture
def sample_employee():
    emp = Employee(
        id=1,
        full_name="Alice Smith",
        email="alice@example.com",
        department="Engineering",
        status=EmployeeStatus.INACTIVE
    )
    return emp

def test_start_onboarding_all_steps_succeed(mock_db, sample_employee):
    mock_db.query().filter().first.return_value = sample_employee

    mock_identity = MagicMock()
    mock_ticketing = MagicMock()
    mock_soap = MagicMock()

    mock_identity.execute.return_value = StepExecutionResult.create_success("Identity created")
    mock_ticketing.execute.return_value = StepExecutionResult.create_success("Tickets created")
    mock_soap.execute.return_value = StepExecutionResult.create_success("HR record updated")

    mock_audit = MagicMock()

    engine_service = WorkflowEngineService(
        audit_service=mock_audit,
        identity_step_executor=mock_identity,
        ticketing_step_executor=mock_ticketing,
        legacy_hr_soap_step_executor=mock_soap
    )

    result = engine_service.start_onboarding(mock_db, 1)

    assert result.status == WorkflowStatus.COMPLETED
    assert sample_employee.status == EmployeeStatus.ACTIVE

    mock_identity.execute.assert_called_once()
    mock_ticketing.execute.assert_called_once()
    mock_soap.execute.assert_called_once()

def test_start_onboarding_middle_step_fails_halts_execution(mock_db, sample_employee):
    mock_db.query().filter().first.return_value = sample_employee

    mock_identity = MagicMock()
    mock_ticketing = MagicMock()
    mock_soap = MagicMock()

    mock_identity.execute.return_value = StepExecutionResult.create_success("Identity created")
    mock_ticketing.execute.return_value = StepExecutionResult.create_failure("Ticketing 503 unavailable")

    mock_audit = MagicMock()

    engine_service = WorkflowEngineService(
        audit_service=mock_audit,
        identity_step_executor=mock_identity,
        ticketing_step_executor=mock_ticketing,
        legacy_hr_soap_step_executor=mock_soap
    )

    result = engine_service.start_onboarding(mock_db, 1)

    assert result.status == WorkflowStatus.FAILED_NEEDS_MANUAL_REVIEW
    mock_identity.execute.assert_called_once()
    mock_ticketing.execute.assert_called_once()
    # Next step (SOAP executor) must NEVER be called
    mock_soap.execute.assert_not_called()

def test_start_onboarding_records_step_transitions_in_order(mock_db, sample_employee):
    mock_db.query().filter().first.return_value = sample_employee

    recorded_step_statuses = []

    def capture_commit():
        # Captures state on each commit
        pass

    mock_db.commit.side_effect = capture_commit

    mock_identity = MagicMock()
    mock_ticketing = MagicMock()
    mock_soap = MagicMock()

    mock_identity.execute.return_value = StepExecutionResult.create_success("Identity created")
    mock_ticketing.execute.return_value = StepExecutionResult.create_failure("Ticketing error")

    mock_audit = MagicMock()

    engine_service = WorkflowEngineService(
        audit_service=mock_audit,
        identity_step_executor=mock_identity,
        ticketing_step_executor=mock_ticketing,
        legacy_hr_soap_step_executor=mock_soap
    )

    result = engine_service.start_onboarding(mock_db, 1)

    assert result.status == WorkflowStatus.FAILED_NEEDS_MANUAL_REVIEW
    # Audit service logs started, step 1 success, step 2 failed, and workflow failed
    logged_events = [c[0][2] for c in mock_audit.log_event.call_args_list]
    assert logged_events == ["WORKFLOW_STARTED", "STEP_SUCCESS", "STEP_FAILED", "WORKFLOW_FAILED"]
