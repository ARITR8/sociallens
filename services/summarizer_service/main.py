import logging
from fastapi import FastAPI
import os

# Set up logging first
from app.core.logging import setup_logging
setup_logging(level="INFO")
logger = logging.getLogger("summarizer_service")

# Debug environment
logger.info(f"🔧 Environment = {os.getenv('ENVIRONMENT')}")
logger.info("🔧 Using Lambda-to-Lambda pattern for database access")

# Now import the rest
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.core.config import settings
from app.api.v1.endpoints.summarizer import router as summarizer_router

# Initialize logging
setup_logging(level="INFO")
logger = logging.getLogger("summarizer_service")

# Create FastAPI app
app = FastAPI(
    title="Summarizer Service",
    description="Microservice for generating summaries from Reddit posts",
    version="1.0.0",
    docs_url="/summarizer/docs",  # ✅ Swagger under base path
    openapi_url="/summarizer/openapi.json"  # ✅ OpenAPI spec path
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health endpoint
@app.get("/summarizer/health")
async def health_check():
    return {"status": "ok", "service": "summarizer", "pattern": "lambda_to_lambda"}

# ✅ Register summarizer routes
app.include_router(
    summarizer_router,
    prefix="/summarizer/api/v1",
    tags=["summarizer"]
)

# ✅ Startup event - no database initialization needed (like reddit fetcher)
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        # With Lambda-to-Lambda pattern, we don't initialize database directly
        logger.info("✅ Using Lambda-to-Lambda pattern for database access")
    except Exception as e:
        # Log the error but don't prevent app startup (like reddit fetcher)
        logger.error(f"❌ Failed to initialize Lambda-to-Lambda pattern: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        # No database connections to close with Lambda-to-Lambda pattern
        logger.info("✅ Shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# ✅ AWS Lambda handler
handler = Mangum(app)

# ✅ Local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)