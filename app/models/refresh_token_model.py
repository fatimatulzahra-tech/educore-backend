from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database.database import Base

class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)

    token = Column(String, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )