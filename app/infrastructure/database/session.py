from app.infrastructure.database import SessionLocal

async def get_session():
    """Dependency function that yields a database session.

    This is used as a FastAPI dependency to provide database sessions
    to endpoint functions. The session is automatically closed after use.
    """
    async with SessionLocal() as session:
        yield session