from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.logging import logger

async def check_database_health() -> bool:
    """Check database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            # Try to execute a simple query
            await session.execute(text("SELECT 1"))
            logger.info("Database health check: OK")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

async def check_schemas_health() -> dict:
    """Check if required database schemas exist."""
    try:
        async with AsyncSessionLocal() as session:
            # Check public schema (where our tables are)
            result = await session.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public'")
            )
            public_exists = bool(result.scalar())

            return {
                "public_schema": "healthy" if public_exists else "missing"
            }
    except Exception as e:
        logger.error(f"Schema health check failed: {str(e)}")
        return {
            "public_schema": "error",
            "error": str(e)
        }
