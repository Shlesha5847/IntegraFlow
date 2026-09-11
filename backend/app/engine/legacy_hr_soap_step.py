import logging
from app.engine.base import StepExecutor, StepExecutionResult
from app.adapters.legacy_hr_soap_adapter import LegacyHrSoapAdapter
from app.models.enums import WorkflowType

logger = logging.getLogger("LegacyHrSoapStepExecutor")

class LegacyHrSoapStepExecutor(StepExecutor):
    def __init__(self, adapter: LegacyHrSoapAdapter = None):
        self.adapter = adapter or LegacyHrSoapAdapter()

    def execute(self, workflow_run, workflow_step) -> StepExecutionResult:
        employee = workflow_run.employee
        target_status = "ACTIVE" if workflow_run.workflow_type == WorkflowType.ONBOARDING else "INACTIVE"
        logger.info(f"Executing Legacy HR SOAP step for run #{workflow_run.id}, employee #{employee.id} -> {target_status}")
        try:
            res = self.adapter.update_employee_status(employee, target_status)
            if res.success:
                return StepExecutionResult.create_success(res.message)
            return StepExecutionResult.create_failure(res.message or "Legacy HR SOAP update failed")
        except Exception as ex:
            logger.error(f"Legacy HR SOAP step failed: {ex}")
            return StepExecutionResult.create_failure(str(ex))
