"""
Service for interacting with the Exa Websets API.

This module contains functions for creating, retrieving, and managing websets
using the Exa Websets API.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from exa_py import Exa
from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters
from app.api.schemas.websets import (
    CreateWebsetRequest,
    WebsetStatus,
    WebsetItem,
    FormattedWebsetItem,
    FormattedEnrichment
)

# Default timeout for waiting for Webset processing (in seconds)
DEFAULT_TIMEOUT = 300  # 5 minutes

async def create_webset(
    exa_client: Exa,
    webset_request: CreateWebsetRequest
) -> WebsetStatus:
    """
    Create a new Webset with the specified search query and enrichments.
    
    Args:
        exa_client: Authenticated Exa client
        webset_request: Webset creation parameters
        
    Returns:
        WebsetStatus: Created Webset object
    """
    try:
        # Extract search parameters from request
        search_query = webset_request.search.query
        search_limit = webset_request.search.count
        
        # Extract enrichment parameters from request
        enrichment_list = webset_request.enrichments
        
        # Create enrichment parameters
        enrichments = []
        for enrichment in enrichment_list:
            enrichments.append(
                CreateEnrichmentParameters(
                    description=enrichment.description,
                    format=enrichment.format,
                )
            )
        
        # Create a Webset with search parameters and enrichments
        webset = exa_client.websets.create(
            params=CreateWebsetParameters(
                search={
                    "query": search_query,
                    "count": search_limit
                },
                enrichments=enrichments,
            )
        )
        
        # Convert to WebsetStatus
        return WebsetStatus(
            id=webset.id,
            status=webset.status,
            created_at=getattr(webset, "created_at", None),
            updated_at=getattr(webset, "updated_at", None),
            search={"query": search_query, "count": search_limit}
        )
    except Exception as e:
        # Re-raise the exception to be handled by the error handler
        raise e

async def get_webset_status(
    exa_client: Exa,
    webset_id: str
) -> WebsetStatus:
    """
    Get the status of a Webset.
    
    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to check
        
    Returns:
        WebsetStatus: Webset status object
    """
    try:
        webset = exa_client.websets.get(webset_id)
        
        # Extract search parameters if available
        search_params = None
        if hasattr(webset, "search"):
            search_params = webset.search
        
        # Convert to WebsetStatus
        return WebsetStatus(
            id=webset.id,
            status=webset.status,
            created_at=getattr(webset, "created_at", None),
            updated_at=getattr(webset, "updated_at", None),
            search=search_params
        )
    except Exception as e:
        # Re-raise the exception to be handled by the error handler
        raise e

async def wait_for_webset_processing(
    exa_client: Exa,
    webset_id: str,
    timeout: int = DEFAULT_TIMEOUT
) -> WebsetStatus:
    """
    Wait for a Webset to finish processing.
    
    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to wait for
        timeout: Maximum time to wait in seconds
        
    Returns:
        WebsetStatus: Updated Webset object
    """
    try:
        start_time = time.time()
        
        # Poll for Webset status until it's idle or timeout is reached
        while True:
            webset = await get_webset_status(exa_client, webset_id)
            
            if webset.status == "idle":
                return webset
            
            # Check if timeout has been reached
            if time.time() - start_time > timeout:
                return webset
            
            # Wait before polling again
            await asyncio.sleep(10)  # Poll every 10 seconds
    except Exception as e:
        # Re-raise the exception to be handled by the error handler
        raise e

async def fetch_webset_items(
    exa_client: Exa,
    webset_id: str
) -> Tuple[List[WebsetItem], int]:
    """
    Fetch items from a Webset.
    
    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to fetch items from
        
    Returns:
        Tuple[List[WebsetItem], int]: List of Webset items and total count
    """
    try:
        # Retrieve Webset Items
        items_response = exa_client.websets.items.list(webset_id=webset_id)
        
        if not items_response.data:
            return [], 0
        
        # Convert to WebsetItem objects
        items = []
        for item in items_response.data:
            # Convert item to dict
            item_dict = {
                "id": item.id,
                "source": item.source,
                "webset_id": item.webset_id,
            }
            
            # Extract properties
            if hasattr(item, "properties"):
                properties = {}
                if hasattr(item.properties, "name"):
                    properties["name"] = item.properties.name
                if hasattr(item.properties, "url"):
                    properties["url"] = item.properties.url
                item_dict["properties"] = properties
            
            # Extract enrichments
            if hasattr(item, "enrichments") and item.enrichments:
                enrichments = []
                for enrichment in item.enrichments:
                    enrichment_dict = {
                        "enrichment_id": getattr(enrichment, "enrichment_id", ""),
                        "format": getattr(enrichment, "format", "text"),
                        "result": getattr(enrichment, "result", ""),
                        "reasoning": getattr(enrichment, "reasoning", None),
                        "references": getattr(enrichment, "references", None),
                    }
                    enrichments.append(enrichment_dict)
                item_dict["enrichments"] = enrichments
            
            items.append(WebsetItem(**item_dict))
        
        return items, len(items)
    except Exception as e:
        # Re-raise the exception to be handled by the error handler
        raise e

async def format_webset_items(
    items: List[WebsetItem]
) -> List[FormattedWebsetItem]:
    """
    Format Webset items with specific fields.
    
    Args:
        items: List of Webset items to format
        
    Returns:
        List[FormattedWebsetItem]: List of formatted Webset items
    """
    if not items:
        return []
    
    # Prepare formatted results
    formatted_results = []
    
    # Map enrichment IDs to field names
    enrichment_id_to_field = {
        "wenrich_cmaqsapcr00crl00itj2ihcx4": "Name",
        "wenrich_cmaqsapcr00csl00iv9o50m44": "Email",
        "wenrich_cmaqsapcr00ctl00iq4gpyqo6": "Phone",
        "wenrich_cmaqsapcr00cul00i3l2dfhq7": "Location",
        "wenrich_cmaqsapcr00cvl00i5p9iokr4": "Company_Name",
        "wenrich_cmaqsapcr00cwl00ij7q5v78o": "Company_Website"
    }
    
    for item in items:
        try:
            # Extract basic item information
            result = {
                "id": item.id,
                "source": item.source,
                "webset_id": item.webset_id
            }
            
            # Extract properties
            if item.properties:
                if hasattr(item.properties, "name"):
                    result["name"] = item.properties.name
                if hasattr(item.properties, "url"):
                    result["url"] = item.properties.url
            
            # Extract enrichments
            if item.enrichments:
                enrichments = {}
                
                for enrichment in item.enrichments:
                    # Skip if no result
                    if not enrichment.result:
                        continue
                    
                    # Get the enrichment ID and result
                    enrichment_id = enrichment.enrichment_id
                    result_value = enrichment.result
                    
                    # Convert list result to string
                    if isinstance(result_value, list) and result_value:
                        result_value = result_value[0]
                    
                    # Try to determine the field from the enrichment ID
                    if enrichment_id in enrichment_id_to_field:
                        field = enrichment_id_to_field[enrichment_id]
                        enrichments[field] = result_value
                        continue
                    
                    # If no match from ID, try to determine from the format
                    enrichment_format = enrichment.format
                    if enrichment_format == "email":
                        enrichments["Email"] = result_value
                    elif enrichment_format == "phone":
                        enrichments["Phone"] = result_value
                    else:
                        # Try to determine from the result content
                        result_str = str(result_value).lower()
                        if "@" in result_str and "." in result_str:
                            enrichments["Email"] = result_value
                        elif "http" in result_str or ".com" in result_str or ".org" in result_str:
                            enrichments["Company_Website"] = result_value
                        elif any(state in result_str for state in ["california", "los angeles", "san francisco"]):
                            enrichments["Location"] = result_value
                
                result["enrichments"] = FormattedEnrichment(**enrichments)
            
            # Add to formatted results
            formatted_results.append(FormattedWebsetItem(**result))
        except Exception as e:
            # Skip items that can't be formatted
            continue
    
    return formatted_results
