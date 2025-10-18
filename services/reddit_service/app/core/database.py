# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings

def get_engine():
    """Create database engine."""
    return create_async_engine(
        Settings().DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        future=True,
        pool_size=5,
        max_overflow=10
    )

engine = get_engine()

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False  # Prevents automatic flushing
)

async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()