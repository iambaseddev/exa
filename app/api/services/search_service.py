"""
Service for interacting with the Exa Search API.

This module contains functions for performing searches using the Exa Search API.
"""

from typing import Dict, List, Any, Optional
from exa_py import Exa
from app.api.schemas.search import SearchRequest, SearchResultMetadata

async def perform_search(
    exa_client: Exa,
    search_request: SearchRequest
) -> List[SearchResultMetadata]:
    """
    Perform a search using the Exa Search API.
    
    Args:
        exa_client: Authenticated Exa client
        search_request: Search request parameters
        
    Returns:
        List[SearchResultMetadata]: List of search results
    """
    try:
        # Perform the search with the specified parameters
        search_response = exa_client.search(
            query=search_request.query,
            num_results=search_request.num_results,
            use_autoprompt=search_request.use_autoprompt,
            include_domains=search_request.include_domains,
            exclude_domains=search_request.exclude_domains,
            start_published_date=search_request.start_published_date,
            end_published_date=search_request.end_published_date,
        )
        
        # Extract results from the response
        search_results = search_response.results
        
        if not search_results:
            return []
        
        # Convert results to SearchResultMetadata objects
        metadata_results = []
        for result in search_results:
            metadata = extract_metadata(result)
            metadata_results.append(SearchResultMetadata(**metadata))
        
        return metadata_results
    except Exception as e:
        # Re-raise the exception to be handled by the error handler
        raise e

def extract_metadata(result) -> Dict[str, Any]:
    """
    Extract metadata from a search result.
    
    Args:
        result: Search result object
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    metadata = {}
    
    # Extract basic metadata using attribute access
    metadata["title"] = getattr(result, "title", "Unknown Title")
    metadata["url"] = getattr(result, "url", "No URL")
    metadata["published_date"] = getattr(result, "published_date", None)
    
    # Extract text snippet
    metadata["text"] = getattr(result, "text", "No text available")
    
    # Extract author information
    if hasattr(result, "author"):
        metadata["author"] = result.author
    else:
        metadata["author"] = None
    
    # Extract other available metadata
    for key in ["source", "score", "id"]:
        if hasattr(result, key):
            metadata[key] = getattr(result, key)
        else:
            metadata[key] = None
    
    return metadata
