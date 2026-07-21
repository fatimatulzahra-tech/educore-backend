from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from datetime import datetime

from app.database.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id"),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    entity = Column(
        String,
        nullable=False
    )

    entity_id = Column(
        Integer,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )