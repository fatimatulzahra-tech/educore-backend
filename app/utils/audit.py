from sqlalchemy.orm import Session

from app.models.audit_log_model import (
    AuditLog
)


def create_audit_log(

    db: Session,

    user_id: int,

    school_id: int,

    action: str,

    entity: str,

    entity_id: int

):

    log = AuditLog(

        user_id=user_id,

        school_id=school_id,

        action=action,

        entity=entity,

        entity_id=entity_id
    )

    db.add(log)
    db.commit()