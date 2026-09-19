"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload

Swagger UI is automatically available at:
    http://localhost:8000/docs
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import auth, students

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Registration System API",
    description="Backend API for registering and listing students.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"] if loc != "body"), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation failed", "errors": errors},
    )


@app.get("/", tags=["Health"])
def root():
    return {"message": "Student Registration System API is running. Visit /docs for Swagger UI."}


app.include_router(students.router)
app.include_router(auth.router)
