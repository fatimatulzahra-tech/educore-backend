from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy import Date
from app.database.database import Base


class Student(Base):

    __tablename__ = "students"

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

    class_id = Column(
        Integer,
        ForeignKey("classes.id"),
        nullable=False
    )

    section_id = Column(
        Integer,
        ForeignKey("sections.id"),
        nullable=False
    )

    first_name = Column(
        String,
        nullable=False
    )

    last_name = Column(
        String,
        nullable=False
    )

    admission_number = Column(
        String,
        nullable=False
    )

    gender = Column(
        String,
        nullable=False
    )

    email = Column(           # ← ADD THIS
        String,
        nullable=True
    )

    phone = Column(
        String,
        nullable=True
    )

    address = Column(
        String,
        nullable=True
    )
    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=True
    )
    admission_date = Column(
        Date,
        nullable=True
        )
    
    date_of_birth = Column(
        Date,
        nullable=True
        )
    
    parent_name = Column(
        String,
        nullable=True
        )
    
    parent_phone = Column(
        String,
        nullable=True
       )