from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='user', nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    groups = relationship(
        'Group',
        secondary='user_group',
        back_populates='users'
    )
