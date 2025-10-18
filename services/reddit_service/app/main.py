from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1.endpoints import fetcher
from app.health.routes import router as health_router
from app.middleware.correlation import CorrelationMiddleware
from app.core.config import Settings
from app.core.database import engine
from app.infrastructure.database.models import Base
from mangum import Mangum



def create_application() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="Reddit Fetcher Service",
        description="Microservice for fetching and filtering Reddit posts",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add correlation ID middleware
    app.add_middleware(CorrelationMiddleware)

    # Add routes
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(
        fetcher.router,
        prefix="/api/v1/fetcher",
        tags=["fetcher"]
    )

    # Add metrics if enabled
    if settings.ENABLE_METRICS:
        Instrumentator().instrument(app).expose(app)

    return app

app = create_application()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Log the error but don't prevent app startup
        print(f"Failed to initialize database: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        # Close database connections
        await engine.dispose()
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")

handler = Mangum(app)