import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import setup_logging
from app.core.config import get_settings
from app.database import init_db, health_check
from app.routes import customers

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting Customer Registry API")
    setup_logging(settings.LOG_LEVEL)
    init_db()
    logger.info(f"Environment: {settings.ENV}, Database: {settings.DATABASE_URL}")
    yield
    # Shutdown
    logger.info("Shutting down Customer Registry API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Customer Registry API",
        description="Internal service for registering and finding business customers",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    
    # Include routes
    app.include_router(customers.router)
    
    # Health check endpoint
    @app.get(
        "/health",
        tags=["operations"],
        summary="Health check",
        description="Service health status",
    )
    def health():
        """Service health check endpoint."""
        db_healthy = health_check()
        status = "healthy" if db_healthy else "degraded"
        return {
            "status": status,
            "service": "customer-registry-api",
            "database": "ok" if db_healthy else "error",
        }
    
    # Root endpoint
    @app.get("/",tags=["operations"], summary="API Information",)
    def root():
        """API root information."""
        return {
            "service": "Customer Registry API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "health": "/health",
        }
    
    # Custom exception handler for validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Format validation errors consistently."""
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {
                    "errors": [
                        {
                            "field": error["loc"][-1] if error["loc"] else "unknown",
                            "message": error["msg"],
                            "type": error["type"],
                        }
                        for error in exc.errors()
                    ]
                },
            },
        )
    
    return app


app = create_app()
