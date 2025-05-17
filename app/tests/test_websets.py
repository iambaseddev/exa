"""
Tests for the websets API endpoints.
"""

import pytest

def test_create_webset_endpoint(client):
    """Test the create webset endpoint."""
    # Define the request payload
    payload = {
        "search": {
            "query": "Test query",
            "count": 3
        },
        "enrichments": [
            {
                "description": "Extract the name of the entrepreneur",
                "format": "text"
            }
        ]
    }

    # Make the request
    response = client.post("/api/websets/", json=payload)

    # Check the response
    assert response.status_code == 201
    assert response.json()["id"] == "webset_123"
    assert response.json()["status"] == "processing"

def test_get_webset_endpoint(mock_get_webset_status):
    """Test the get webset endpoint."""
    # Make the request
    response = client.get("/api/websets/webset_123")

    # Check the response
    assert response.status_code == 200
    assert response.json()["id"] == "webset_123"
    assert response.json()["status"] == "processing"

def test_wait_for_webset_endpoint(mock_wait_for_webset_processing):
    """Test the wait for webset endpoint."""
    # Make the request
    response = client.get("/api/websets/webset_123/wait?timeout=10")

    # Check the response
    assert response.status_code == 200
    assert response.json()["id"] == "webset_123"
    assert response.json()["status"] == "idle"

def test_get_webset_items_endpoint(mock_fetch_webset_items):
    """Test the get webset items endpoint."""
    # Make the request
    response = client.get("/api/websets/webset_123/items")

    # Check the response
    assert response.status_code == 200
    assert response.json()["webset_id"] == "webset_123"
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["id"] == "witem_123"

def test_get_formatted_webset_items_endpoint(mock_fetch_webset_items, mock_format_webset_items):
    """Test the get formatted webset items endpoint."""
    # Make the request
    response = client.get("/api/websets/webset_123/formatted")

    # Check the response
    assert response.status_code == 200
    assert response.json()["webset_id"] == "webset_123"
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["id"] == "witem_123"
