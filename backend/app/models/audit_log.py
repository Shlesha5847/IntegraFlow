from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    workflow_run_id = Column(BigInteger, ForeignKey("workflow_run.id"), nullable=False)
    event = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    workflow_run = relationship("WorkflowRun", back_populates="audit_logs")
