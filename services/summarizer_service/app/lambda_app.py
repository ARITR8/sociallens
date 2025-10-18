from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.core.logging import setup_logging, logger
from app.api.v1.endpoints.summarizer import router as summarizer_router
import os

# Setup logging first
setup_logging(level=os.getenv('LOG_LEVEL', 'INFO'))

logger.info("Starting summarizer application initialization")

# Create FastAPI app (following reddit fetcher pattern)
app = FastAPI(
    title="Summarizer Service",
    description="Service for generating summaries from Reddit posts",
    version="1.0.0"
    # No custom docs_url - use default /docs
)

# Add CORS middleware (following reddit fetcher pattern)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health endpoint (following reddit fetcher pattern)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "summarizer",
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "function_name": os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'local'),
        "version": "1.0.0"
    }

# Add routes (following reddit fetcher pattern)
app.include_router(
    summarizer_router,
    prefix="/api/v1/summarizer",
    tags=["summarizer"]
)

# Wrap with Lambda handler (following reddit fetcher pattern)
handler = Mangum(app)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Summarizer application starting up")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Summarizer application shutting down")