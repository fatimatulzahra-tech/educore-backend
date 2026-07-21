from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)

from app.database.database import Base


class FeePlan(Base):

    __tablename__ = "fee_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )