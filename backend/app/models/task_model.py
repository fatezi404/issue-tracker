from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, ForeignKey, column
from sqlalchemy.orm import relationship

from app.db.session import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String, default='new', nullable=False)
    priority = Column(String, nullable=True)
    assignee_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True) # note: ispolnitel
    reporter_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True) # note: sozdatel
    is_done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship(
        'Group',
        back_populates='tasks'
    )
    assignee = relationship('User', foreign_keys=[assignee_id], back_populates='assigned_tasks')
    reporter = relationship('User', foreign_keys=[reporter_id], back_populates='reported_tasks')
