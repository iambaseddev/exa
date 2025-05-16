#!/usr/bin/env python3
"""
Tests for Excel Export Utility

This module tests the functionality of the Excel export utility.
"""

import os
import json
import pandas as pd
import pytest
from src.utils.excel_export import json_to_excel, search_results_to_excel


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {
        "results": [
            {
                "id": "witem_01jvcj1fhwy2c68zxyy2c68zxy",
                "source": "search",
                "webset_id": "webset_cmaqsk393000tlq0icayjcwg0",
                "url": "https://www.linkedin.com/in/jan-mccarthy-4872517",
                "enrichments": {
                    "Company Website": "https://www.janmccarthy.com",
                    "Location": "Los Angeles, California",
                    "Email": "tkgcareofbusiness@gmail.com",
                    "Phone": "3039562712"
                }
            },
            {
                "id": "witem_01jvcj1ggy0mydqpj00mydqpj0",
                "source": "search",
                "webset_id": "webset_cmaqsk393000tlq0icayjcwg0",
                "url": "https://www.linkedin.com/in/sheila-thorne-3867a576",
                "enrichments": {
                    "Company Website": "https://www.woce.us",
                    "Location": "Palos Verdes Peninsula, California"
                    # Note: Missing Phone field
                }
            }
        ]
    }


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        {
            "title": "OpenAI",
            "url": "https://openai.com/",
            "published_date": "2025-05-05T00:00:00.000Z",
            "author": "OpenAI Team",
            "source": "openai.com",
            "score": 0.95,
            "text": "OpenAI is an AI research lab consisting of the for-profit company OpenAI LP and its parent company, the non-profit OpenAI Inc."
        },
        {
            "title": "Anthropic",
            "url": "https://www.anthropic.com/",
            "published_date": "2025-03-27T00:00:00.000Z",
            # Note: Missing author field
            "source": "anthropic.com",
            "score": 0.85,
            "text": "Anthropic is an AI safety company that's working to build reliable, interpretable, and steerable AI systems."
        }
    ]


def test_json_to_excel(sample_json_data, tmp_path):
    """Test converting JSON data to Excel format."""
    # Create a temporary JSON file
    json_file = tmp_path / "test_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_json_data, f)

    # Convert to Excel
    excel_file = json_to_excel(sample_json_data, str(json_file))

    # Check that the Excel file was created
    assert os.path.exists(excel_file)

    # Read the Excel file and check its contents
    df = pd.read_excel(excel_file)

    # Check that we have the right number of rows
    assert len(df) == 2

    # Check that the columns include both basic fields and enrichments
    expected_columns = ['id', 'source', 'webset_id', 'url', 'Company Website', 'Location', 'Email', 'Phone']
    for col in expected_columns:
        assert col in df.columns

    # Check that the data was correctly transferred
    assert df.iloc[0]['id'] == "witem_01jvcj1fhwy2c68zxyy2c68zxy"
    assert df.iloc[0]['Email'] == "tkgcareofbusiness@gmail.com"
    # Phone should contain the correct digits, regardless of format
    phone = str(df.iloc[0]['Phone']).strip()
    assert phone.replace('.0', '').replace('.', '') == "3039562712"

    # Check that missing fields are empty (not filled with NaN)
    # The second record is missing the Phone field
    assert pd.isna(df.iloc[1]['Phone']) or df.iloc[1]['Phone'] == ""


def test_search_results_to_excel(sample_search_results, tmp_path):
    """Test converting search results to Excel format."""
    # Create a temporary text file
    text_file = tmp_path / "test_search.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("Test search results")

    # Convert to Excel
    query = "AI research labs"
    excel_file = search_results_to_excel(sample_search_results, query, str(text_file))

    # Check that the Excel file was created
    assert os.path.exists(excel_file)

    # Read the Excel file and check its contents
    df = pd.read_excel(excel_file)

    # Check that we have the right number of rows
    assert len(df) == 2

    # Check that the columns include all expected fields
    expected_columns = ['title', 'url', 'published_date', 'author', 'source', 'score', 'text']
    for col in expected_columns:
        assert col in df.columns

    # Check that the data was correctly transferred
    assert df.iloc[0]['title'] == "OpenAI"
    assert df.iloc[0]['author'] == "OpenAI Team"

    # Check that missing fields are empty (not filled with NaN)
    # The second record is missing the author field
    assert pd.isna(df.iloc[1]['author']) or df.iloc[1]['author'] == ""


def test_json_to_excel_empty_data():
    """Test handling of empty data."""
    # Test with empty results
    empty_data = {"results": []}
    result = json_to_excel(empty_data, "test_empty.json")
    assert result == ""


def test_search_results_to_excel_empty_data():
    """Test handling of empty search results."""
    # Test with empty results
    empty_results = []
    result = search_results_to_excel(empty_results, "test query", "test_empty.txt")
    assert result is None
