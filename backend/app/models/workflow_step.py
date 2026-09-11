from sqlalchemy import Column, BigInteger, Integer, String, Text, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.enums import StepStatus, IntegrationType

class WorkflowStep(Base):
    __tablename__ = "workflow_step"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    workflow_run_id = Column(BigInteger, ForeignKey("workflow_run.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    integration_type = Column(SQLEnum(IntegrationType, name="integration_type_enum", native_enum=False), nullable=False)
    status = Column(SQLEnum(StepStatus, name="step_status_enum", native_enum=False), nullable=False, default=StepStatus.PENDING)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, nullable=True)

    workflow_run = relationship("WorkflowRun", back_populates="steps")
