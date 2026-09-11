import logging
from app.engine.base import StepExecutor, StepExecutionResult
from app.adapters.identity_adapter import IdentityRestAdapter
from app.models.enums import WorkflowType

logger = logging.getLogger("IdentityStepExecutor")

class IdentityStepExecutor(StepExecutor):
    def __init__(self, adapter: IdentityRestAdapter = None):
        self.adapter = adapter or IdentityRestAdapter()

    def execute(self, workflow_run, workflow_step) -> StepExecutionResult:
        employee = workflow_run.employee
        logger.info(f"Executing Identity step for run #{workflow_run.id}, employee #{employee.id}")
        try:
            if workflow_run.workflow_type == WorkflowType.ONBOARDING:
                res = self.adapter.create_identity_account(employee)
            else:
                res = self.adapter.deactivate_identity_account(employee)

            if res.success:
                return StepExecutionResult.create_success(res.message)
            return StepExecutionResult.create_failure(res.message or "Identity operation failed")
        except Exception as ex:
            logger.error(f"Identity step failed: {ex}")
            return StepExecutionResult.create_failure(str(ex))
