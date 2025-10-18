from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def check_database_health(session: AsyncSession) -> bool:
    """Check database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        await session.commit()
        return True
    except Exception:
        return False