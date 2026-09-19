"""
SQLAlchemy ORM model(s).

This defines the `students` table structure in Python. SQLAlchemy uses
this class to generate SQL for creating the table and for every
query/insert performed through the ORM.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), nullable=False, unique=True, index=True)
    mobile = Column(String(10), nullable=False, unique=True, index=True)

    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    course = Column(String(10), nullable=False)

    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(6), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
