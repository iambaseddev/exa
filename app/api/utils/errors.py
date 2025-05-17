"""
Error handling utilities for the API.

This module contains functions and classes for handling errors in a consistent way.
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class ExaAPIError(HTTPException):
    """
    Custom exception for Exa API errors.
    
    This exception is raised when there is an error with the Exa API.
    """
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "An error occurred with the Exa API",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

def handle_exa_error(error: Exception) -> ExaAPIError:
    """
    Handle an error from the Exa API and convert it to an appropriate HTTPException.
    
    Args:
        error: The exception raised by the Exa API
        
    Returns:
        ExaAPIError: An HTTPException with an appropriate status code and message
    """
    # Determine the appropriate status code based on the error
    if "not found" in str(error).lower() or "does not exist" in str(error).lower():
        status_code = status.HTTP_404_NOT_FOUND
    elif "unauthorized" in str(error).lower() or "authentication" in str(error).lower():
        status_code = status.HTTP_401_UNAUTHORIZED
    elif "forbidden" in str(error).lower() or "permission" in str(error).lower():
        status_code = status.HTTP_403_FORBIDDEN
    elif "invalid" in str(error).lower() or "bad request" in str(error).lower():
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return ExaAPIError(
        status_code=status_code,
        detail=f"Exa API error: {str(error)}"
    )
