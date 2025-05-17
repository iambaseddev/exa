"""
Tests for the search API endpoints.
"""

import pytest

def test_search_endpoint(client):
    """Test the search endpoint."""
    # Define the request payload
    payload = {
        "query": "Test query",
        "num_results": 3,
        "use_autoprompt": True
    }

    # Make the request
    response = client.post("/api/search/", json=payload)

    # Check the response
    assert response.status_code == 200
    assert response.json()["query"] == "Test query"
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["title"] == "Test Title"
    assert response.json()["results"][0]["url"] == "https://example.com"

def test_search_endpoint_with_all_parameters(client):
    """Test the search endpoint with all parameters."""
    # Define the request payload
    payload = {
        "query": "Test query",
        "num_results": 5,
        "use_autoprompt": False,
        "include_domains": ["example.com"],
        "exclude_domains": ["exclude.com"],
        "start_published_date": "2023-01-01",
        "end_published_date": "2023-12-31"
    }

    # Make the request
    response = client.post("/api/search/", json=payload)

    # Check the response
    assert response.status_code == 200

def test_search_endpoint_with_error(client, mock_dependencies):
    """Test the search endpoint with an error."""
    # Configure the mock to raise an exception
    mock_dependencies["perform_search"].side_effect = Exception("Test error")

    # Define the request payload
    payload = {
        "query": "Test query",
        "num_results": 3,
        "use_autoprompt": True
    }

    # Make the request
    response = client.post("/api/search/", json=payload)

    # Check the response
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]
