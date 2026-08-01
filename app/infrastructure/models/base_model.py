from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.
    
    This provides the common declarative base for all ORM models,
    enabling automatic table metadata generation and ORM functionality.
    """
    pass