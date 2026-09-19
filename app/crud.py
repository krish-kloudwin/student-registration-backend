"""
CRUD (Create / Read) functions.

This layer talks directly to the database through SQLAlchemy. Keeping
these functions separate from the API route functions (in main.py) keeps
the code easy to read and easy to test.
"""
from sqlalchemy.orm import Session

from app import models, schemas


def get_student_by_email(db: Session, email: str) -> models.Student | None:
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_student_by_mobile(db: Session, mobile: str) -> models.Student | None:
    return db.query(models.Student).filter(models.Student.mobile == mobile).first()


def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(db: Session, skip: int = 0, limit: int = 100) -> list[models.Student]:
    return (
        db.query(models.Student)
        .order_by(models.Student.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
