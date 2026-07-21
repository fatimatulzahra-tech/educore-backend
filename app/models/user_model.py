from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer,ForeignKey("schools.id"),nullable=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String,default="user")
    is_verified = Column(Boolean,default=False)
    verification_token = Column(String,nullable=True)
    reset_token = Column(String,nullable=True)
    is_first_login = Column(Boolean, default=True)