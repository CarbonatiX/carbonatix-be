from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from .database import get_db
from .router import router


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, field: str = None, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()
    if db is not None:
        _ensure_indexes(db)
        from .seed import seed_database
        seed_database(db)
    yield


def _ensure_indexes(db):
    db.users.create_index("email", unique=True)
    db.companies.create_index("owner_user_id", unique=True)
    db.twin_models.create_index("company_id")
    db.documents.create_index("company_id")
    db.calculation_runs.create_index("company_id")
    db.calculation_runs.create_index([("company_id", 1), ("created_at", -1)])
    db.recommendations.create_index("run_id")
    db.recommendations.create_index([("company_id", 1), ("run_id", 1)])
    db.forecasts.create_index("updated_at")


app = FastAPI(title="CarbonatiX", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    body = {"error": {"code": exc.code, "message": exc.message}}
    if exc.field:
        body["error"]["field"] = exc.field
    if exc.details:
        body["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first.get("loc", []))
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": first.get("msg", "Validation error"),
                "field": field or None,
            }
        },
    )


app.include_router(router)
