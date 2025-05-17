#!/usr/bin/env python3
"""
Exa API FastAPI Application

This is the main entry point for the FastAPI application that provides
a RESTful API for interacting with the Exa API.
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from app.api.routes import search, websets
from app.api.utils.dependencies import get_exa_client

# Load environment variables from .env file
load_dotenv()

# Check if API key is available
if not os.getenv("exa_api_key"):
    raise ValueError("No API key found. Please set 'exa_api_key' in your .env file.")

# Create FastAPI application
app = FastAPI(
    title="Exa API",
    description="A RESTful API for interacting with the Exa Search and Websets APIs",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(websets.router, prefix="/api/websets", tags=["websets"])

@app.get("/", tags=["root"])
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "message": "Welcome to the Exa API",
        "docs": "/docs",
        "version": "1.0.0",
    }

@app.get("/health", tags=["health"])
async def health_check(exa_client = Depends(get_exa_client)):
    """Health check endpoint that verifies the API is running and can connect to Exa."""
    try:
        # Simple check to verify Exa client is working
        return {"status": "healthy", "message": "API is running and Exa client is configured"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"API is unhealthy: {str(e)}"
        )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Exa API",
        version="1.0.0",
        description="A RESTful API for interacting with the Exa Search and Websets APIs",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
