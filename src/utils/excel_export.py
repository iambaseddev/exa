#!/usr/bin/env python3
"""
Excel Export Utility

This module provides functions to export data to Excel/Google Sheets format.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional


def ensure_results_dir(base_dir: str = "../results") -> str:
    """
    Ensure the results directory exists.

    Args:
        base_dir: Base directory for results

    Returns:
        str: Path to the results directory
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir


def json_to_excel(
    data: Dict[str, List[Dict[str, Any]]],
    output_file: str,
    sheet_name: str = "Results"
) -> str:
    """
    Convert JSON data to Excel format and save to file.

    Args:
        data: JSON data to convert (expected format: {"results": [...]})
        output_file: Output file path for JSON (will be modified for Excel)
        sheet_name: Name of the sheet in the Excel file

    Returns:
        str: Path to the saved Excel file
    """
    # Extract results from data
    results = data.get("results", [])
    if not results:
        return ""

    # Create a list to hold flattened data
    flattened_data = []

    # Process each result
    for result in results:
        # Start with basic fields
        flat_result = {
            "id": result.get("id", ""),
            "source": result.get("source", ""),
            "webset_id": result.get("webset_id", ""),
            "url": result.get("url", "")
        }

        # Add enrichments if available
        enrichments = result.get("enrichments", {})
        for field, value in enrichments.items():
            # Handle list values by taking the first item
            if isinstance(value, list) and value:
                flat_result[field] = value[0]
            else:
                flat_result[field] = value

        flattened_data.append(flat_result)

    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)

    # Convert numeric-looking strings to strings to prevent auto-conversion
    for col in df.columns:
        if col in ['Phone', 'Email']:
            # Convert to string and remove decimal point and zeros for numeric values
            df[col] = df[col].apply(lambda x: str(int(float(x))) if pd.notnull(x) and str(x).replace('.', '').isdigit() else x)

    # Generate Excel file path from JSON path
    excel_file = output_file.replace(".json", ".xlsx")

    # Save to Excel
    df.to_excel(excel_file, sheet_name=sheet_name, index=False)

    return excel_file


def search_results_to_excel(
    results: List[Dict[str, Any]],
    query: str,
    output_file: Optional[str] = None
) -> Optional[str]:
    """
    Convert search results to Excel format and save to file.

    Args:
        results: List of search results
        query: The search query used
        output_file: Optional file path to save results to

    Returns:
        Optional[str]: Path to the saved Excel file or None if no output file
    """
    if not results or not output_file:
        return None

    # Create a list to hold flattened data
    flattened_data = []

    # Process each result
    for result in results:
        # Extract metadata
        metadata = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "published_date": result.get("published_date", ""),
            "author": result.get("author", ""),
            "source": result.get("source", ""),
            "score": result.get("score", ""),
            "text": result.get("text", "")[:300]  # Truncate text to a reasonable length
        }

        flattened_data.append(metadata)

    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)

    # Generate Excel file path from text path
    excel_file = output_file.replace(".txt", ".xlsx")

    # Save to Excel - replace invalid characters in sheet name
    safe_query = query[:30].replace(':', '-').replace('/', '-').replace('\\', '-').replace('?', '-').replace('*', '-').replace('[', '(').replace(']', ')')
    df.to_excel(excel_file, sheet_name=f"Search {safe_query}", index=False)

    return excel_file
