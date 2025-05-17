#!/usr/bin/env python3
"""
Exa API Script

This script fetches and displays specific details from the Exa API.
It demonstrates how to:
1. Authenticate with the Exa API
2. Perform a search using the Exa Search API
3. Format and display search results with specific fields
4. Handle potential errors and edge cases

Usage:
    Make sure you have a .env file with your Exa API key:
    exa_api_key=your_api_key

    Run the script:
    python webset_fetcher.py [--query "Your search query"]

    The script will perform a search and display the results.
"""

import os
import sys
import argparse
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from exa_py import Exa
from src.utils.excel_export import search_results_to_excel

# Maximum number of items to display
MAX_ITEMS = 3

# Default search query
DEFAULT_SEARCH_QUERY = "Top AI research labs focusing on large language models"

# API base URL - can be modified if the API endpoint changes
API_BASE_URL = "https://api.exa.ai"

def setup_exa_client() -> Optional[Exa]:
    """
    Set up and return an authenticated Exa client.

    Returns:
        Exa: Authenticated Exa client or None if authentication fails
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('exa_api_key')

    if not api_key:
        print("Error: No API key found. Please set 'exa_api_key' in your .env file.")
        return None

    try:
        # Initialize Exa client with API key and custom base URL if needed
        client = Exa(api_key)

        # Optionally set a custom API base URL if the default doesn't work
        # Uncomment the following line if needed:
        # client.websets.base_url = API_BASE_URL

        print(f"Exa client initialized successfully with API key: {api_key[:4]}...{api_key[-4:]}")
        return client
    except Exception as e:
        print(f"Error initializing Exa client: {e}")
        return None

def perform_search(exa_client: Exa, query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Perform a search using the Exa Search API.

    Args:
        exa_client: Authenticated Exa client
        query: Search query

    Returns:
        List: List of search results or None if search fails
    """
    try:
        print(f"Performing search for: {query}")

        # Perform the search with the specified query and limit
        search_response = exa_client.search(
            query=query,
            num_results=MAX_ITEMS,
            use_autoprompt=True,  # Enable autoprompt for better results
            include_domains=None,  # No domain restrictions
            exclude_domains=None,  # No domain exclusions
            start_published_date=None,  # No date restrictions
            end_published_date=None,
        )

        # Extract results from the response
        search_results = search_response.results

        if not search_results:
            print("No search results found.")
            return []

        print(f"Found {len(search_results)} search results.")
        return search_results
    except Exception as e:
        print(f"Error performing search: {e}")
        return None

def extract_metadata(result) -> Dict[str, Any]:
    """
    Extract metadata from a search result.

    Args:
        result: Search result object

    Returns:
        Dict: Extracted metadata
    """
    metadata = {}

    # Extract basic metadata using attribute access
    metadata["title"] = getattr(result, "title", "Unknown Title")
    metadata["url"] = getattr(result, "url", "No URL")
    metadata["published_date"] = getattr(result, "published_date", "Unknown Date")

    # Extract text snippet
    metadata["text"] = getattr(result, "text", "No text available")

    # Extract author information
    if hasattr(result, "author"):
        metadata["author"] = result.author

    # Extract other available metadata
    for key in ["source", "score", "id"]:
        if hasattr(result, key):
            metadata[key] = getattr(result, key)

    return metadata

def format_and_display_results(results: List[Dict[str, Any]], query: str, output_file: Optional[str] = None) -> None:
    """
    Format and display search results with specific fields.

    Args:
        results: List of search results to display
        query: The search query used
        output_file: Optional file path to save results to
    """
    if not results:
        print("No results to display.")
        return

    # Prepare output lines
    output_lines = []
    output_lines.append("="*80)
    output_lines.append(f"DISPLAYING TOP {len(results)} RESULTS FOR: {query}")
    output_lines.append("="*80)

    for i, result in enumerate(results, 1):
        try:
            # Extract metadata from the result
            metadata = extract_metadata(result)

            # Format result
            output_lines.append(f"\nRESULT {i}:")
            output_lines.append(f"Title: {metadata['title']}")
            output_lines.append(f"URL: {metadata['url']}")

            # Add publication date if available
            if "published_date" in metadata and metadata["published_date"]:
                output_lines.append(f"Published: {metadata['published_date']}")

            # Add author if available
            if "author" in metadata and metadata["author"]:
                output_lines.append(f"Author: {metadata['author']}")

            # Add source if available
            if "source" in metadata and metadata["source"]:
                output_lines.append(f"Source: {metadata['source']}")

            # Add score if available
            if "score" in metadata and metadata["score"]:
                output_lines.append(f"Relevance Score: {metadata['score']}")

            # Add text snippet
            if "text" in metadata and metadata["text"]:
                # Truncate text to a reasonable length
                text = metadata["text"]
                max_length = 300
                if len(text) > max_length:
                    text = text[:max_length] + "..."
                output_lines.append(f"\nExcerpt: {text}")

            output_lines.append("-"*80)
        except Exception as e:
            output_lines.append(f"Error displaying result {i}: {e}")
            output_lines.append("-"*80)

    # Join all lines
    output_text = "\n".join(output_lines)

    # Print to console
    print("\n" + output_text)

    # Save to file if requested
    if output_file:
        try:
            # Save to text file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\nResults saved to {output_file}")

            # Save to Excel file
            try:
                # Extract metadata for Excel export
                excel_data = [extract_metadata(result) for result in results]
                excel_file = search_results_to_excel(excel_data, query, output_file)
                if excel_file:
                    print(f"Results also saved to Excel file: {excel_file}")
            except Exception as e:
                print(f"Error saving results to Excel file: {e}")
        except Exception as e:
            print(f"Error saving results to file: {e}")

def main():
    """Main function to execute the script."""
    global MAX_ITEMS

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch and display Exa Search API data")
    parser.add_argument("--query", type=str, help="Search query to use")
    parser.add_argument("--output", "-o", type=str, default="../results/search_results.txt", help="Output file to save results to")
    parser.add_argument("--limit", "-l", type=int, default=MAX_ITEMS,
                        help=f"Maximum number of results to display (default: {MAX_ITEMS})")
    args = parser.parse_args()

    # Set up Exa client
    exa_client = setup_exa_client()
    if not exa_client:
        sys.exit(1)

    # Use provided query or default
    query = args.query if args.query else DEFAULT_SEARCH_QUERY

    # Update MAX_ITEMS if limit is provided
    if args.limit:
        MAX_ITEMS = args.limit

    # Perform search
    results = perform_search(exa_client, query)
    if results is None:
        sys.exit(1)

    # Format and display results
    format_and_display_results(results, query, args.output)

if __name__ == "__main__":
    main()
