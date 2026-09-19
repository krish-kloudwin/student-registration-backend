"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload

Swagger UI is automatically available at:
    http://localhost:8000/docs
"""
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.database import Base, engine, get_db

# Create all tables on startup if they do not already exist.
# (For this assignment, database/schema.sql is the primary/authoritative
# way to create the schema - this line is a convenience so the app also
# works immediately even if that script was not run manually.)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Registration System API",
    description="Backend API for registering and listing students.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS configuration
#
# The browser treats http://localhost:3000 (Next.js) and http://localhost:8000
# (FastAPI) as two different "origins" because the port numbers differ, even
# though both run on the same machine. Browsers block cross-origin requests
# by default (Same-Origin Policy). Without CORS configured here, the
# frontend's fetch()/axios calls to the backend would be blocked by the
# browser with a CORS error. This middleware tells the browser it is safe
# to allow requests from the listed origins.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers - keep error responses clean and consistent,
# and never leak raw database/SQL error text to the client.
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Triggered automatically when Pydantic validation fails
    (e.g. invalid email, invalid course, short name, etc.).
    Returns HTTP 422 with a readable list of field errors.
    """
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"] if loc != "body"), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation failed", "errors": errors},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    return {"message": "Student Registration System API is running. Visit /docs for Swagger UI."}


@app.post(
    "/api/students",
    response_model=schemas.StudentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
    summary="Register a new student",
)
def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Registers a new student.

    - Runs Pydantic validation automatically (field formats, ranges, allowed values).
    - Runs business validation (duplicate email / duplicate mobile) below.
    - Persists the record to PostgreSQL through SQLAlchemy.
    """
    # --- Business validation: duplicate checks -----------------------------
    if crud.get_student_by_email(db, student.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email is already registered",
        )

    if crud.get_student_by_mobile(db, student.mobile):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this mobile number is already registered",
        )

    try:
        db_student = crud.create_student(db, student)
    except IntegrityError:
        # Safety net: catches a race condition where two identical requests
        # arrive at the same time and both pass the checks above. The raw
        # database error is never sent to the client.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email or mobile number is already registered",
        )

    return schemas.StudentRegisterResponse(
        success=True,
        message="Student registered successfully",
        student_id=db_student.id,
    )


@app.get(
    "/api/students",
    response_model=list[schemas.StudentResponse],
    tags=["Students"],
    summary="List all registered students",
)
def list_students(db: Session = Depends(get_db)):
    """Returns all registered students, most recently registered first."""
    return crud.get_students(db)
