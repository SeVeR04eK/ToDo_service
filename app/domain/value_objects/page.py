from dataclasses import dataclass
from typing import TypeVar, Generic, List

T = TypeVar('T')


@dataclass(frozen=True)
class Page(Generic[T]):
    """Generic paginated result domain model.
    
    This domain model represents a paginated collection of items with metadata
    about the pagination state. It is used throughout the domain and application
    layers to pass paginated results without depending on HTTP-specific concepts.
    
    Attributes:
        items: List of items for the current page
        page: Current page number (1-indexed)
        page_size: Number of items per page
        total_items: Total number of items matching the query
        total_pages: Total number of pages available
        has_next: Whether there is a next page
        has_previous: Whether there is a previous page
    """
    items: List[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        page: int,
        page_size: int,
        total_items: int
    ) -> "Page[T]":
        """Create a Page instance from raw pagination data.
        
        Args:
            items: List of items for the current page
            page: Current page number (1-indexed)
            page_size: Number of items per page
            total_items: Total number of items matching the query
            
        Returns:
            A Page instance with calculated pagination metadata
        """
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
