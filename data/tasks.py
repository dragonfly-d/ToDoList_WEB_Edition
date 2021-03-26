import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase


class Tasks(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=True)

    created_date = Column(DateTime, default=datetime.datetime.now)

    done = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relation('User')
    priority = Column(Integer, default=4)
    scheduled_date = Column(DateTime, default=datetime.datetime.now().date())
