"""
Pydantic schemas.

These define the shape and validation rules for data going IN to the API
(requests) and OUT of the API (responses). This is the "Pydantic
Validation" layer in the architecture diagram - it runs automatically,
before any of our own business logic, on every request.
"""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# Allowed dropdown values (also enforced by the frontend, but the backend
# is the real source of truth).
Gender = Literal["Male", "Female", "Other"]
Course = Literal["BCA", "BSc", "BCom", "MCA", "MBA"]


class StudentCreate(BaseModel):
    """Validates the incoming JSON body for POST /api/students."""

    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile: str
    date_of_birth: date
    gender: Gender
    course: Course
    address: str = Field(..., min_length=10, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str

    # --- Field-level validators -------------------------------------------------

    @field_validator("first_name", "last_name", "city", "state", "address")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty or only whitespace")
        return value

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: str) -> str:
        value = value.strip()
        # Indian mobile numbers: exactly 10 digits, first digit 6-9.
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        if value[0] not in ("6", "7", "8", "9"):
            raise ValueError(
                "Mobile number must be a valid Indian mobile number "
                "(must start with 6, 7, 8, or 9)"
            )
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit() or len(value) != 6:
            raise ValueError("Pincode must be exactly 6 digits")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")

        today = date.today()
        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )
        if age < 5:
            raise ValueError("Student must be at least 5 years old")
        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Rahul",
                "last_name": "Kumar",
                "email": "rahul@gmail.com",
                "mobile": "9876543210",
                "date_of_birth": "2002-05-15",
                "gender": "Male",
                "course": "BCA",
                "address": "123 MG Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "pincode": "560001",
            }
        }
    }


class StudentResponse(BaseModel):
    """Shape of a single student record returned by GET /api/students."""

    id: int
    first_name: str
    last_name: str
    email: str
    mobile: str
    date_of_birth: date
    gender: str
    course: str
    address: str
    city: str
    state: str
    pincode: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # allows creation from ORM objects


class StudentRegisterResponse(BaseModel):
    """Shape of the response returned right after a successful registration."""

    success: bool
    message: str
    student_id: int


class ErrorResponse(BaseModel):
    """Generic clean error response shape used for 409 / 4xx errors."""

    success: bool = False
    message: str
    detail: Optional[str] = None


# --- Auth schemas ------------------------------------------------------------


class AdminLogin(BaseModel):
    """Request body for POST /api/v1/auth/login."""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class AdminLoginResponse(BaseModel):
    """Response body after a successful login.

    The token is set as an httpOnly cookie (used automatically by the
    Next.js frontend) AND returned here in the body as a Bearer token -
    copy this value into Swagger's "Authorize" button to test protected
    routes directly from /docs."""

    success: bool
    message: str
    username: str
    access_token: str
    token_type: str = "bearer"


class AdminMeResponse(BaseModel):
    """Response body for GET /api/v1/auth/me - who is currently logged in."""

    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
