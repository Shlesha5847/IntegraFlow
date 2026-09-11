from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
from app.models.enums import IntegrationType

@dataclass
class StepExecutionResult:
    success: bool
    message: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def create_success(cls, message: str) -> "StepExecutionResult":
        return cls(success=True, message=message, error_message=None)

    @classmethod
    def create_failure(cls, error_message: str) -> "StepExecutionResult":
        return cls(success=False, message=None, error_message=error_message)

class StepExecutor(ABC):
    @abstractmethod
    def execute(self, workflow_run, workflow_step) -> StepExecutionResult:
        pass

@dataclass
class WorkflowStepDefinition:
    step_order: int
    step_name: str
    integration_type: IntegrationType
    step_executor: StepExecutor
