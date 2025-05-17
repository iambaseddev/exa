"""
Routes for the search API.

This module contains FastAPI route handlers for the search API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from exa_py import Exa

from app.api.utils.dependencies import get_exa_client
from app.api.utils.errors import handle_exa_error
from app.api.schemas.search import SearchRequest, SearchResponse
from app.api.services.search_service import perform_search

router = APIRouter()

@router.post("/", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search(
    search_request: SearchRequest,
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Perform a search using the Exa Search API.
    
    Args:
        search_request: Search request parameters
        exa_client: Authenticated Exa client
        
    Returns:
        SearchResponse: Search results
    """
    try:
        results = await perform_search(exa_client, search_request)
        
        return SearchResponse(
            query=search_request.query,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        raise handle_exa_error(e)
