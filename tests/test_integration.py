#!/usr/bin/env python3
"""
Integration Tests for Exa API Scripts

This module tests the integration of Excel export functionality with the main scripts.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
sys.path.insert(0, '.')  # Add the current directory to the path

# Import the functions to test
from src.exa_websets import format_and_save_results as websets_format_and_save
from src.check_webset import format_and_save_results as check_webset_format_and_save
from src.exa_search import format_and_display_results


@pytest.fixture
def sample_webset_items():
    """Sample Webset items for testing."""
    # Create a mock item with the necessary attributes
    item1 = MagicMock()
    item1.id = "witem_01jvcj1fhwy2c68zxyy2c68zxy"
    item1.source = "search"
    item1.webset_id = "webset_cmaqsk393000tlq0icayjcwg0"

    # Mock properties
    properties = MagicMock()
    properties.url = "https://www.linkedin.com/in/jan-mccarthy-4872517"
    item1.properties = properties

    # Mock enrichments
    enrichment1 = MagicMock()
    enrichment1.enrichment_id = "wenrich_cmaqsapcr00csl00iv9o50m44"
    enrichment1.format = "email"
    enrichment1.result = "tkgcareofbusiness@gmail.com"
    enrichment1.__str__ = lambda self: "tkgcareofbusiness@gmail.com"

    enrichment2 = MagicMock()
    enrichment2.enrichment_id = "wenrich_cmaqsapcr00ctl00iq4gpyqo6"
    enrichment2.format = "phone"
    enrichment2.result = "3039562712"
    enrichment2.__str__ = lambda self: "3039562712"

    enrichment3 = MagicMock()
    enrichment3.enrichment_id = "wenrich_cmaqsapcr00cul00i3l2dfhq7"
    enrichment3.format = "text"
    enrichment3.result = "Los Angeles, California"
    enrichment3.__str__ = lambda self: "Los Angeles, California"

    item1.enrichments = [enrichment1, enrichment2, enrichment3]

    # Create a second item with missing fields
    item2 = MagicMock()
    item2.id = "witem_01jvcj1ggy0mydqpj00mydqpj0"
    item2.source = "search"
    item2.webset_id = "webset_cmaqsk393000tlq0icayjcwg0"

    # Mock properties
    properties2 = MagicMock()
    properties2.url = "https://www.linkedin.com/in/sheila-thorne-3867a576"
    item2.properties = properties2

    # Mock enrichments - missing phone
    enrichment4 = MagicMock()
    enrichment4.enrichment_id = "wenrich_cmaqsapcr00cwl00ij7q5v78o"
    enrichment4.format = "url"
    enrichment4.result = "https://www.woce.us"
    enrichment4.__str__ = lambda self: "https://www.woce.us"

    enrichment5 = MagicMock()
    enrichment5.enrichment_id = "wenrich_cmaqsapcr00cul00i3l2dfhq7"
    enrichment5.format = "text"
    enrichment5.result = "Palos Verdes Peninsula, California"
    enrichment5.__str__ = lambda self: "Palos Verdes Peninsula, California"

    item2.enrichments = [enrichment4, enrichment5]

    return [item1, item2]


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    # Create mock search results
    result1 = MagicMock()
    result1.title = "OpenAI"
    result1.url = "https://openai.com/"
    result1.published_date = "2025-05-05T00:00:00.000Z"
    result1.author = "OpenAI Team"
    result1.source = "openai.com"
    result1.score = 0.95
    result1.text = "OpenAI is an AI research lab consisting of the for-profit company OpenAI LP and its parent company, the non-profit OpenAI Inc."

    result2 = MagicMock()
    result2.title = "Anthropic"
    result2.url = "https://www.anthropic.com/"
    result2.published_date = "2025-03-27T00:00:00.000Z"
    # Missing author field
    result2.source = "anthropic.com"
    result2.score = 0.85
    result2.text = "Anthropic is an AI safety company that's working to build reliable, interpretable, and steerable AI systems."

    return [result1, result2]


@pytest.fixture
def config():
    """Sample configuration for testing."""
    return {
        "enrichments": [
            "Name",
            "Email",
            "Phone",
            "Location",
            "Company Name",
            "Company Website"
        ]
    }


def test_websets_format_and_save_results(sample_webset_items, config, tmp_path):
    """Test that websets format_and_save_results creates JSON files."""
    # Create output file path
    output_file = str(tmp_path / "test_websets_results.json")

    # Call the function with mocked json_to_excel to avoid actual Excel file creation
    with patch('src.utils.excel_export.json_to_excel', return_value="mock.xlsx"):
        with patch('builtins.print'):  # Suppress print statements
            websets_format_and_save(sample_webset_items, config, output_file)

    # Check that the JSON file was created
    assert os.path.exists(output_file)


def test_check_webset_format_and_save_results(sample_webset_items, config, tmp_path):
    """Test that check_webset format_and_save_results creates JSON files."""
    # Create output file path
    output_file = str(tmp_path / "test_check_webset_results.json")

    # Call the function with mocked json_to_excel to avoid actual Excel file creation
    with patch('src.utils.excel_export.json_to_excel', return_value="mock.xlsx"):
        with patch('builtins.print'):  # Suppress print statements
            check_webset_format_and_save(sample_webset_items, config, output_file)

    # Check that the JSON file was created
    assert os.path.exists(output_file)


def test_search_format_and_display_results(sample_search_results, tmp_path):
    """Test that search format_and_display_results creates text files."""
    # Create output file path
    output_file = str(tmp_path / "test_search_results.txt")

    # Call the function with mocked search_results_to_excel to avoid actual Excel file creation
    with patch('src.utils.excel_export.search_results_to_excel', return_value="mock.xlsx"):
        with patch('builtins.print'):  # Suppress print statements
            format_and_display_results(sample_search_results, "Test query", output_file)

    # Check that the text file was created
    assert os.path.exists(output_file)

    # Check text content
    with open(output_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    assert "OpenAI" in text_content
    assert "Anthropic" in text_content
