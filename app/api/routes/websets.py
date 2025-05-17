"""
Routes for the websets API.

This module contains FastAPI route handlers for the websets API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from exa_py import Exa

from app.api.utils.dependencies import get_exa_client
from app.api.utils.errors import handle_exa_error
from app.api.schemas.websets import (
    CreateWebsetRequest,
    WebsetStatus,
    WebsetItemsResponse,
    FormattedWebsetItemsResponse
)
from app.api.services.webset_service import (
    create_webset,
    get_webset_status,
    wait_for_webset_processing,
    fetch_webset_items,
    format_webset_items
)

router = APIRouter()

@router.post("/", response_model=WebsetStatus, status_code=status.HTTP_201_CREATED)
async def create_new_webset(
    webset_request: CreateWebsetRequest,
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Create a new Webset with the specified search query and enrichments.
    
    Args:
        webset_request: Webset creation parameters
        exa_client: Authenticated Exa client
        
    Returns:
        WebsetStatus: Created Webset object
    """
    try:
        webset = await create_webset(exa_client, webset_request)
        return webset
    except Exception as e:
        raise handle_exa_error(e)

@router.get("/{webset_id}", response_model=WebsetStatus, status_code=status.HTTP_200_OK)
async def get_webset(
    webset_id: str = Path(..., description="ID of the Webset to check"),
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Get the status of a Webset.
    
    Args:
        webset_id: ID of the Webset to check
        exa_client: Authenticated Exa client
        
    Returns:
        WebsetStatus: Webset status object
    """
    try:
        webset = await get_webset_status(exa_client, webset_id)
        return webset
    except Exception as e:
        raise handle_exa_error(e)

@router.get("/{webset_id}/wait", response_model=WebsetStatus, status_code=status.HTTP_200_OK)
async def wait_for_webset(
    webset_id: str = Path(..., description="ID of the Webset to wait for"),
    timeout: int = Query(300, description="Maximum time to wait in seconds"),
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Wait for a Webset to finish processing.
    
    Args:
        webset_id: ID of the Webset to wait for
        timeout: Maximum time to wait in seconds
        exa_client: Authenticated Exa client
        
    Returns:
        WebsetStatus: Updated Webset object
    """
    try:
        webset = await wait_for_webset_processing(exa_client, webset_id, timeout)
        return webset
    except Exception as e:
        raise handle_exa_error(e)

@router.get("/{webset_id}/items", response_model=WebsetItemsResponse, status_code=status.HTTP_200_OK)
async def get_webset_items(
    webset_id: str = Path(..., description="ID of the Webset to fetch items from"),
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Fetch items from a Webset.
    
    Args:
        webset_id: ID of the Webset to fetch items from
        exa_client: Authenticated Exa client
        
    Returns:
        WebsetItemsResponse: List of Webset items
    """
    try:
        items, total = await fetch_webset_items(exa_client, webset_id)
        
        return WebsetItemsResponse(
            items=items,
            total=total,
            webset_id=webset_id
        )
    except Exception as e:
        raise handle_exa_error(e)

@router.get("/{webset_id}/formatted", response_model=FormattedWebsetItemsResponse, status_code=status.HTTP_200_OK)
async def get_formatted_webset_items(
    webset_id: str = Path(..., description="ID of the Webset to fetch items from"),
    exa_client: Exa = Depends(get_exa_client)
):
    """
    Fetch and format items from a Webset.
    
    Args:
        webset_id: ID of the Webset to fetch items from
        exa_client: Authenticated Exa client
        
    Returns:
        FormattedWebsetItemsResponse: List of formatted Webset items
    """
    try:
        items, total = await fetch_webset_items(exa_client, webset_id)
        formatted_items = await format_webset_items(items)
        
        return FormattedWebsetItemsResponse(
            results=formatted_items,
            total=total,
            webset_id=webset_id
        )
    except Exception as e:
        raise handle_exa_error(e)
