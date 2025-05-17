"""
Pytest configuration file for the tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set environment variables for testing
os.environ["exa_api_key"] = "test_api_key"

# Import app after setting environment variables
from app.main import app

@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def mock_dependencies():
    """
    Mock all external dependencies.
    """
    # Mock the get_exa_client dependency
    with patch("app.api.utils.dependencies.get_exa_client") as _:
        # Mock the search service
        with patch("app.api.services.search_service.perform_search") as mock_perform_search:
            # Create a mock search result
            mock_result = {
                "title": "Test Title",
                "url": "https://example.com",
                "text": "Test text content",
                "published_date": "2023-01-01",
                "author": "Test Author",
                "source": "Test Source",
                "score": 0.95,
                "id": "result_123"
            }
            
            # Configure the mock to return a valid response
            mock_perform_search.return_value = [mock_result]
            
            # Mock the webset services
            with patch("app.api.services.webset_service.create_webset") as mock_create_webset:
                mock_create_webset.return_value = {
                    "id": "webset_123",
                    "status": "processing",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                    "search": {"query": "Test query", "count": 3}
                }
                
                with patch("app.api.services.webset_service.get_webset_status") as mock_get_webset_status:
                    mock_get_webset_status.return_value = {
                        "id": "webset_123",
                        "status": "processing",
                        "created_at": "2023-01-01T12:00:00Z",
                        "updated_at": "2023-01-01T12:00:00Z",
                        "search": {"query": "Test query", "count": 3}
                    }
                    
                    with patch("app.api.services.webset_service.wait_for_webset_processing") as mock_wait_for_webset_processing:
                        mock_wait_for_webset_processing.return_value = {
                            "id": "webset_123",
                            "status": "idle",
                            "created_at": "2023-01-01T12:00:00Z",
                            "updated_at": "2023-01-01T12:05:00Z",
                            "search": {"query": "Test query", "count": 3}
                        }
                        
                        with patch("app.api.services.webset_service.fetch_webset_items") as mock_fetch_webset_items:
                            mock_item = {
                                "id": "witem_123",
                                "source": "search",
                                "webset_id": "webset_123",
                                "properties": {
                                    "name": "Test Item",
                                    "url": "https://example.com"
                                },
                                "enrichments": [
                                    {
                                        "enrichment_id": "wenrich_123",
                                        "format": "text",
                                        "result": "Test Result",
                                        "reasoning": "Test Reasoning",
                                        "references": None
                                    }
                                ]
                            }
                            mock_fetch_webset_items.return_value = ([mock_item], 1)
                            
                            with patch("app.api.services.webset_service.format_webset_items") as mock_format_webset_items:
                                mock_formatted_item = {
                                    "id": "witem_123",
                                    "source": "search",
                                    "webset_id": "webset_123",
                                    "name": "Test Item",
                                    "url": "https://example.com",
                                    "enrichments": {
                                        "Name": "Test Result"
                                    }
                                }
                                mock_format_webset_items.return_value = [mock_formatted_item]
                                
                                yield {
                                    "perform_search": mock_perform_search,
                                    "create_webset": mock_create_webset,
                                    "get_webset_status": mock_get_webset_status,
                                    "wait_for_webset_processing": mock_wait_for_webset_processing,
                                    "fetch_webset_items": mock_fetch_webset_items,
                                    "format_webset_items": mock_format_webset_items
                                }
