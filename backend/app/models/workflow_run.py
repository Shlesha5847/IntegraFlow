from sqlalchemy import Column, BigInteger, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.enums import WorkflowType, WorkflowStatus

class WorkflowRun(Base):
    __tablename__ = "workflow_run"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employee.id"), nullable=False)
    workflow_type = Column(SQLEnum(WorkflowType, name="workflow_type_enum", native_enum=False), nullable=False)
    status = Column(SQLEnum(WorkflowStatus, name="workflow_status_enum", native_enum=False), nullable=False, default=WorkflowStatus.IN_PROGRESS)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    employee = relationship("Employee")
    steps = relationship("WorkflowStep", back_populates="workflow_run", order_by="WorkflowStep.step_order")
    audit_logs = relationship("AuditLog", back_populates="workflow_run", order_by="AuditLog.created_at")
