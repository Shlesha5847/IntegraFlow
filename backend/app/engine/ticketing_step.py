import logging
from app.engine.base import StepExecutor, StepExecutionResult
from app.adapters.ticketing_adapter import TicketingRestAdapter
from app.models.enums import WorkflowType

logger = logging.getLogger("TicketingStepExecutor")

class TicketingStepExecutor(StepExecutor):
    def __init__(self, adapter: TicketingRestAdapter = None):
        self.adapter = adapter or TicketingRestAdapter()

    def execute(self, workflow_run, workflow_step) -> StepExecutionResult:
        employee = workflow_run.employee
        logger.info(f"Executing Ticketing step for run #{workflow_run.id}, employee #{employee.id}")
        try:
            if workflow_run.workflow_type == WorkflowType.ONBOARDING:
                res = self.adapter.create_onboarding_tickets(employee)
            else:
                res = self.adapter.close_all_tickets(employee)

            if res.success:
                return StepExecutionResult.create_success(res.message)
            return StepExecutionResult.create_failure(res.message or "Ticketing operation failed")
        except Exception as ex:
            logger.error(f"Ticketing step failed: {ex}")
            return StepExecutionResult.create_failure(str(ex))
