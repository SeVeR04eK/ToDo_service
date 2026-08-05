from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Any

T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata for API responses."""
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items matching the query")
    total_pages: int = Field(..., description="Total number of pages available")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class DataResponse(BaseModel, Generic[T]):
    """Generic single-item response wrapper for API endpoints.
    
    This model provides a consistent response format for all single-item endpoints.
    It wraps a single item in a 'data' field.
    
    Type Parameters:
        T: The type of the single item
        
    Example:
        {
            "data": {
                "id": 1,
                "username": "user@example.com"
            }
        }
    """
    data: T = Field(..., description="The response data")


class ListResponse(BaseModel, Generic[T]):
    """Generic list response wrapper for API endpoints.
    
    This model provides a consistent response format for all non-paginated collection endpoints.
    It wraps a list of items in a 'data' field.
    
    Type Parameters:
        T: The type of items in the collection
        
    Example:
        {
            "data": [
                {"id": 1, "username": "user1@example.com"},
                {"id": 2, "username": "user2@example.com"}
            ]
        }
    """
    data: List[T] = Field(..., description="List of items")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper for API endpoints.
    
    This model provides a consistent response format for all paginated endpoints.
    It wraps a list of items with pagination metadata.
    
    Type Parameters:
        T: The type of items in the collection
        
    Example:
        {
            "data": [{"id": 1, "title": "Task 1"}, {"id": 2, "title": "Task 2"}],
            "meta": {
                "page": 1,
                "limit": 20,
                "total_items": 157,
                "total_pages": 8,
                "has_next": true,
                "has_previous": false
            }
        }
    """
    data: List[T] = Field(..., description="List of items for the current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
