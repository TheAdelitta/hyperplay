from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.labs import SOURCE_HEADER
from app.api.labs import router as labs_router
from app.api.simulations import router as simulations_router
from app.core.config import get_settings
from app.core.errors import ApiError, api_error_handler

settings = get_settings()
app = FastAPI(
    title="Hyperplay API",
    version="1.0.0",
    description="Turns educational material into validated interactive simulation specs.",
)
app.add_exception_handler(ApiError, api_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=[SOURCE_HEADER],
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(simulations_router, prefix="/api/v1")
app.include_router(labs_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"name": "Hyperplay API", "docs": "/docs"}
