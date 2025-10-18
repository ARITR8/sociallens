from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.core.logging import setup_logging, logger
from app.core.database import init_db, AsyncSessionLocal
from app.api.v1.endpoints import data
from sqlalchemy import text
import os

# Setup logging first
setup_logging(level=os.getenv('LOG_LEVEL', 'INFO'))

# Check database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL environment variable is missing")
    raise ValueError("DATABASE_URL environment variable is required")

logger.info("Starting application initialization")
logger.info(f"Database host: {database_url.split('@')[1].split('/')[0]}")  # Log only host:port

# Create FastAPI app
app = FastAPI(
    title="Data Service",
    description="Centralized database service for all microservices",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    data.router,
    prefix="/api/v1",
    tags=["data"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "function_name": os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'local'),
        "version": "1.0.0"
    }

# Wrap with Lambda handler
handler = Mangum(
    app,
    lifespan="off"
)

# Add Lambda wrapper for better logging
from app.lambda_handler import lambda_handler_wrapper
handler = lambda_handler_wrapper(handler)

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    try:
        # Initialize database
        await init_db()
        db_status = "initialized"
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        db_status = "failed"

    logger.info(
        "Application starting up",
        extra={
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'function_name': os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'local'),
            'function_version': os.getenv('AWS_LAMBDA_FUNCTION_VERSION', 'local'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'database_status': db_status,
            'database_configured': bool(database_url)
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(
        "Application shutting down",
        extra={
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'function_name': os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'local')
        }
    )