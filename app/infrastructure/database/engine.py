from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core import settings


# Create async engine for database connections
# echo=True enables SQL logging in debug mode
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Session factory for creating database sessions
# expire_on_commit=False prevents objects from being expired after commit
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)