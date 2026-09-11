import enum

class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class WorkflowType(str, enum.Enum):
    ONBOARDING = "ONBOARDING"
    OFFBOARDING = "OFFBOARDING"

class WorkflowStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED_NEEDS_MANUAL_REVIEW = "FAILED_NEEDS_MANUAL_REVIEW"

class StepStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class IntegrationType(str, enum.Enum):
    REST = "REST"
    SOAP = "SOAP"
