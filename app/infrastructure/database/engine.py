from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core import settings


# Create async engine for database connections
# echo=True enables SQL logging in debug mode
# Connection pooling parameters only apply to PostgreSQL, not SQLite
engine_kwargs = {"echo": settings.debug}

# Apply connection pooling only for PostgreSQL (not SQLite)
if "postgresql" in settings.database_url or "postgres" in settings.database_url:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # Recycle connections after 1 hour
    })

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Session factory for creating database sessions
# expire_on_commit=False prevents objects from being expired after commit
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)