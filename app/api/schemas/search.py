"""
Pydantic schemas for the search API.

This module contains Pydantic models for validating request and response data
for the search API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl

class SearchRequest(BaseModel):
    """
    Schema for a search request.
    """
    query: str = Field(..., description="The search query to use")
    num_results: int = Field(3, description="Maximum number of results to return", ge=1, le=100)
    use_autoprompt: bool = Field(True, description="Whether to use autoprompt for better results")
    include_domains: Optional[List[str]] = Field(None, description="List of domains to include in search results")
    exclude_domains: Optional[List[str]] = Field(None, description="List of domains to exclude from search results")
    start_published_date: Optional[str] = Field(None, description="Start date for filtering results (ISO format)")
    end_published_date: Optional[str] = Field(None, description="End date for filtering results (ISO format)")

class SearchResultMetadata(BaseModel):
    """
    Schema for search result metadata.
    """
    title: str = Field(..., description="Title of the search result")
    url: HttpUrl = Field(..., description="URL of the search result")
    published_date: Optional[str] = Field(None, description="Publication date of the search result")
    author: Optional[str] = Field(None, description="Author of the search result")
    source: Optional[str] = Field(None, description="Source of the search result")
    score: Optional[float] = Field(None, description="Relevance score of the search result")
    text: str = Field(..., description="Text excerpt from the search result")
    id: Optional[str] = Field(None, description="Unique identifier for the search result")

class SearchResponse(BaseModel):
    """
    Schema for a search response.
    """
    query: str = Field(..., description="The search query that was used")
    results: List[SearchResultMetadata] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results found")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Top AI research labs focusing on large language models",
                "results": [
                    {
                        "title": "Top AI Research Labs in 2023",
                        "url": "https://example.com/ai-labs",
                        "published_date": "2023-01-15",
                        "author": "John Doe",
                        "source": "AI News",
                        "score": 0.95,
                        "text": "This article covers the top AI research labs focusing on large language models...",
                        "id": "result_123456"
                    }
                ],
                "total_results": 1
            }
        }
