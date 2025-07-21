from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.session import Base


user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    users = relationship(
        'User',
        secondary='user_group',
        back_populates='groups',
    )
    tasks = relationship(
        'Task',
        back_populates='group'
    )
