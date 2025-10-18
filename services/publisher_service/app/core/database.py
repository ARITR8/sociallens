from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.schema import CreateSchema
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import logger
from typing import Dict

# Create async engine - FIXED: Removed connect_args options
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            # Set search path directly in session
            await session.execute(text("SET search_path TO public"))
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()

# Database initialization
async def init_db():
    """Initialize database."""
    try:
        async with engine.begin() as conn:
            # Ensure we're in public schema
            await conn.execute(text("SET search_path TO public"))
            
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
            
            # Log schema information
            result = await conn.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            logger.info("Available tables in public schema:")
            for table in tables:
                logger.info(f"- {table.table_name}")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

# Utility function to check database health
async def check_db_connection() -> bool:
    """Check database connection health."""
    try:
        async with AsyncSessionLocal() as session:
            # Test basic query
            await session.execute(text("SELECT 1"))
            
            # Check if story_summaries table exists
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'story_summaries'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.warning("story_summaries table not found in public schema")
            else:
                logger.info("story_summaries table found in public schema")
            
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# Utility function to check schema setup
async def check_schema_setup() -> Dict[str, str]:
    """Check schema setup and table locations."""
    try:
        async with AsyncSessionLocal() as session:
            # Check table locations
            result = await session.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name IN ('story_summaries', 'published_articles')
            """))
            tables = result.fetchall()
            
            schema_info = {}
            for table in tables:
                schema_info[table.table_name] = table.table_schema
            
            return schema_info
            
    except Exception as e:
        logger.error(f"Schema check failed: {str(e)}")
        raise
