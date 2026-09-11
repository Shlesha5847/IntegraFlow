from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.workflow_run import WorkflowRun
from datetime import datetime
import logging

logger = logging.getLogger("AuditService")

class AuditService:
    def log_event(self, db: Session, workflow_run: WorkflowRun, event: str, detail: str) -> AuditLog:
        logger.info(f"[AUDIT] Run #{workflow_run.id}: {event} - {detail}")
        audit = AuditLog(
            workflow_run_id=workflow_run.id,
            event=event,
            detail=detail,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    def get_audit_logs_for_run(self, db: Session, workflow_run_id: int):
        return db.query(AuditLog).filter(AuditLog.workflow_run_id == workflow_run_id).order_by(AuditLog.created_at.asc()).all()
