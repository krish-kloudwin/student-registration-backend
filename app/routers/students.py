"""
Student routes - API version 1.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/v1/students", tags=["Students (v1)"])


@router.post(
    "",
    response_model=schemas.StudentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student",
)
def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """Public endpoint - no login required to register."""
    if crud.get_student_by_email(db, student.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A student with this email is already registered")

    if crud.get_student_by_mobile(db, student.mobile):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A student with this mobile number is already registered")

    try:
        db_student = crud.create_student(db, student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A student with this email or mobile number is already registered")

    return schemas.StudentRegisterResponse(success=True, message="Student registered successfully", student_id=db_student.id)


@router.get(
    "",
    response_model=list[schemas.StudentResponse],
    summary="List all registered students (admin only)",
)
def list_students(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    """Requires a valid admin login."""
    return crud.get_students(db)
