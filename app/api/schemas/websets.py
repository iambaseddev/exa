"""
Pydantic schemas for the websets API.

This module contains Pydantic models for validating request and response data
for the websets API endpoints.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator

class EnrichmentParameter(BaseModel):
    """
    Schema for an enrichment parameter.
    """
    description: str = Field(..., description="Detailed description of what to extract")
    format: str = Field("text", description="Format of the enrichment (text, email, phone, etc.)")

class SearchParameter(BaseModel):
    """
    Schema for search parameters in a webset.
    """
    query: str = Field(..., description="The search query to use")
    count: int = Field(3, description="Maximum number of results to return", ge=1, le=100)

class CreateWebsetRequest(BaseModel):
    """
    Schema for creating a new webset.
    """
    search: SearchParameter = Field(..., description="Search parameters for the webset")
    enrichments: List[EnrichmentParameter] = Field(..., description="List of enrichments to apply to search results")

class WebsetStatus(BaseModel):
    """
    Schema for webset status.
    """
    id: str = Field(..., description="Unique identifier for the webset")
    status: str = Field(..., description="Current status of the webset (e.g., 'idle', 'processing')")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    search: Optional[Dict[str, Any]] = Field(None, description="Search parameters used for the webset")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "webset_cmaqrbpy900b5mk0ialbn5z07",
                "status": "idle",
                "created_at": "2023-01-15T12:00:00Z",
                "updated_at": "2023-01-15T12:05:00Z",
                "search": {
                    "query": "entrepreneur (founder, co-founder, or owner of a business) currently resides in the usa",
                    "count": 3
                }
            }
        }

class EnrichmentResult(BaseModel):
    """
    Schema for an enrichment result.
    """
    enrichment_id: str = Field(..., description="ID of the enrichment")
    format: str = Field(..., description="Format of the enrichment")
    result: Union[str, List[str]] = Field(..., description="Result of the enrichment")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the enrichment result")
    references: Optional[List[Dict[str, Any]]] = Field(None, description="References used for the enrichment")

class ItemProperties(BaseModel):
    """
    Schema for item properties.
    """
    name: Optional[str] = Field(None, description="Name of the item")
    url: Optional[HttpUrl] = Field(None, description="URL of the item")

class WebsetItem(BaseModel):
    """
    Schema for a webset item.
    """
    id: str = Field(..., description="Unique identifier for the item")
    source: str = Field(..., description="Source of the item")
    webset_id: str = Field(..., description="ID of the webset the item belongs to")
    properties: Optional[ItemProperties] = Field(None, description="Properties of the item")
    enrichments: Optional[List[EnrichmentResult]] = Field(None, description="Enrichment results for the item")

class WebsetItemsResponse(BaseModel):
    """
    Schema for a response containing webset items.
    """
    items: List[WebsetItem] = Field(..., description="List of webset items")
    total: int = Field(..., description="Total number of items")
    webset_id: str = Field(..., description="ID of the webset")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "witem_01jvcg32bdreggpdvrreggpdvr",
                        "source": "search",
                        "webset_id": "webset_cmaqrbpy900b5mk0ialbn5z07",
                        "properties": {
                            "name": "Example Item",
                            "url": "https://example.com"
                        },
                        "enrichments": [
                            {
                                "enrichment_id": "wenrich_cmaqsapcr00crl00itj2ihcx4",
                                "format": "text",
                                "result": "John Doe",
                                "reasoning": "This is the name of the entrepreneur."
                            }
                        ]
                    }
                ],
                "total": 1,
                "webset_id": "webset_cmaqrbpy900b5mk0ialbn5z07"
            }
        }

class FormattedEnrichment(BaseModel):
    """
    Schema for a formatted enrichment result.
    """
    Name: Optional[str] = Field(None, description="Name of the entrepreneur")
    Email: Optional[str] = Field(None, description="Email address of the entrepreneur")
    Phone: Optional[str] = Field(None, description="Phone number of the entrepreneur")
    Location: Optional[str] = Field(None, description="Location of the entrepreneur")
    Company_Name: Optional[str] = Field(None, description="Name of the entrepreneur's company")
    Company_Website: Optional[HttpUrl] = Field(None, description="Website of the entrepreneur's company")

class FormattedWebsetItem(BaseModel):
    """
    Schema for a formatted webset item.
    """
    id: str = Field(..., description="Unique identifier for the item")
    source: str = Field(..., description="Source of the item")
    webset_id: str = Field(..., description="ID of the webset the item belongs to")
    name: Optional[str] = Field(None, description="Name of the item")
    url: Optional[HttpUrl] = Field(None, description="URL of the item")
    enrichments: Optional[FormattedEnrichment] = Field(None, description="Formatted enrichment results")

class FormattedWebsetItemsResponse(BaseModel):
    """
    Schema for a response containing formatted webset items.
    """
    results: List[FormattedWebsetItem] = Field(..., description="List of formatted webset items")
    total: int = Field(..., description="Total number of items")
    webset_id: str = Field(..., description="ID of the webset")
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "witem_01jvcg32bdreggpdvrreggpdvr",
                        "source": "search",
                        "webset_id": "webset_cmaqrbpy900b5mk0ialbn5z07",
                        "name": "Example Item",
                        "url": "https://example.com",
                        "enrichments": {
                            "Name": "John Doe",
                            "Email": "john@example.com",
                            "Phone": "+1234567890",
                            "Location": "San Francisco, CA",
                            "Company_Name": "Example Inc.",
                            "Company_Website": "https://example.com"
                        }
                    }
                ],
                "total": 1,
                "webset_id": "webset_cmaqrbpy900b5mk0ialbn5z07"
            }
        }
