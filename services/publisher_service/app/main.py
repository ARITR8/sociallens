import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.v1.endpoints import publisher
from app.health import routes as health_routes

# Setup logging with colors and formatting
setup_logging(level=settings.LOG_LEVEL)
logger = logging.getLogger("publisher_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up publisher service...")
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Log configuration
        logger.info("\n=== Service Configuration ===")
        logger.info(f"Service Name: {settings.SERVICE_NAME}")
        logger.info(f"WordPress API URL: {settings.WP_API_URL}")
        logger.info(f"WordPress Username: {settings.WP_USERNAME}")
        logger.info(f"Bedrock Model: {settings.BEDROCK_MODEL_ID}")
        logger.info(f"Database: {settings.POSTGRES_DB}")
        logger.info(f"Schema: {settings.POSTGRES_SCHEMA}")
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down publisher service...")

# Create FastAPI app
app = FastAPI(
    title="Publisher Service",
    description="Service for publishing AI-generated articles to WordPress",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    publisher.router,
    prefix=settings.API_V1_STR,
    tags=["publisher"]
)

app.include_router(health_routes.router, tags=["health"])

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "description": "Publisher service for creating and publishing AI-generated articles",
        "features": [
            "AI-powered article generation",
            "WordPress integration",
            "SEO optimization",
            "Automated publishing"
        ],
        "docs_url": "/docs",
        "health_check": "/health",
        "metrics": "/metrics" if settings.ENABLE_METRICS else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
