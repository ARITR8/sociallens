from fastapi import APIRouter, Depends
from app.infrastructure.wordpress.client import WordPressClient
from app.infrastructure.llm.factory import create_llm_client  # Changed: use factory
from app.health.database import check_database_health, check_schemas_health
from app.core.logging import logger

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    # Initialize clients
    wp_client = WordPressClient()
    llm_client = create_llm_client()  # Changed: use factory

    # Check all components
    db_health = await check_database_health()
    schemas_health = await check_schemas_health()
    wp_health = await wp_client.check_api_status()
    
    # Check LLM health (if the client has a health check method)
    try:
        # Note: BaseLLMClient doesn't have check_model_status yet
        # For now, just check if client initialized successfully
        llm_health = llm_client is not None
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        llm_health = False

    # Determine overall status
    all_healthy = all([
        db_health,
        schemas_health["publisher_schema"] == "healthy",
        schemas_health["summarizer_schema"] == "healthy",
        wp_health,
        llm_health
    ])

    health_status = {
        "status": "healthy" if all_healthy else "unhealthy",
        "components": {
            "database": {
                "status": "healthy" if db_health else "unhealthy",
                "schemas": schemas_health
            },
            "wordpress_api": {
                "status": "healthy" if wp_health else "unhealthy"
            },
            "llm_service": {
                "status": "healthy" if llm_health else "unhealthy",
                "provider": llm_client.__class__.__name__ if llm_health else "unknown"
            }
        }
    }

    # Log health check results
    logger.info(f"Health check results: {health_status}")
    
    return health_status

@router.get("/health/database")
async def database_health():
    """Specific database health check."""
    return {
        "database": await check_database_health(),
        "schemas": await check_schemas_health()
    }

@router.get("/health/wordpress")
async def wordpress_health():
    """Specific WordPress API health check."""
    wp_client = WordPressClient()
    is_healthy = await wp_client.check_api_status()
    return {
        "status": "healthy" if is_healthy else "unhealthy"
    }

@router.get("/health/llm")
async def llm_health():
    """Specific LLM service health check."""
    try:
        llm_client = create_llm_client()  # Changed: use factory
        # Simple check: if client initialized, it's healthy
        is_healthy = llm_client is not None
        provider = llm_client.__class__.__name__
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        is_healthy = False
        provider = "unknown"
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "provider": provider
    }
