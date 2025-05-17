"""
Dependencies for FastAPI routes.

This module contains dependency functions that can be used with FastAPI's
dependency injection system.
"""

import os
from typing import Optional
from fastapi import HTTPException, status
from exa_py import Exa

def get_exa_client() -> Exa:
    """
    Dependency that provides an authenticated Exa client.
    
    Returns:
        Exa: Authenticated Exa client
        
    Raises:
        HTTPException: If authentication fails
    """
    # Get API key from environment
    api_key = os.getenv('exa_api_key')
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No API key found. Please set 'exa_api_key' in your .env file."
        )
    
    try:
        # Initialize Exa client with API key
        client = Exa(api_key)
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing Exa client: {str(e)}"
        )
