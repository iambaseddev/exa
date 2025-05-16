#!/usr/bin/env python3
"""
Exa Websets API Script

This script uses the Exa Websets API to search for entrepreneurs in the USA
and enrich the results with specific data points like contact information
and company details.

Usage:
    Make sure you have a .env file with your Exa API key:
    exa_api_key=your_api_key

    Run the script:
    python exa_websets.py [--config config.json] [--output results.json]
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from exa_py import Exa
from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters

# Default timeout for waiting for Webset processing (in seconds)
TIMEOUT = 300  # 5 minutes

def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        config_file: Path to the configuration file

    Returns:
        Dict: Configuration data
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Configuration loaded from {config_file}")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration")
        return {
            "search": {
                "query": "entrepreneur (founder, co-founder, or owner of a business) currently resides in the usa",
                "limit": 3
            },
            "enrichments": [
                "Name",
                "Email",
                "Phone",
                "Location",
                "Company Name",
                "Company Website"
            ]
        }

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
        # Initialize Exa client with API key
        client = Exa(api_key)
        print(f"Exa client initialized successfully with API key: {api_key[:4]}...{api_key[-4:]}")
        return client
    except Exception as e:
        print(f"Error initializing Exa client: {e}")
        return None

def create_webset(exa_client: Exa, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new Webset with the specified search query and enrichments.

    Args:
        exa_client: Authenticated Exa client
        config: Configuration data

    Returns:
        Dict: Created Webset object or None if creation fails
    """
    try:
        # Extract search parameters from config
        search_query = config["search"]["query"]
        search_limit = config["search"].get("limit", 3)

        # Extract enrichment parameters from config
        enrichment_list = config.get("enrichments", [])

        # Create enrichment parameters
        enrichments = []
        for enrichment in enrichment_list:
            # Determine the appropriate format based on the enrichment type
            format_type = "text"
            if enrichment.lower() == "email":
                format_type = "email"
            elif enrichment.lower() == "phone":
                format_type = "phone"

            # Create a detailed description for the enrichment
            description = f"Extract the {enrichment} of the entrepreneur"
            if enrichment.lower() == "name":
                description = "Extract the full name of the entrepreneur (founder, co-founder, or business owner)"
            elif enrichment.lower() == "email":
                description = "Extract the email address of the entrepreneur for contact purposes"
            elif enrichment.lower() == "phone":
                description = "Extract the phone number of the entrepreneur or their business"
            elif enrichment.lower() == "location":
                description = "Extract the location (city, state) where the entrepreneur currently resides"
            elif enrichment.lower() == "company name":
                description = "Extract the name of the company or business founded by the entrepreneur"
            elif enrichment.lower() == "company website":
                description = "Extract the website URL of the entrepreneur's company or business"

            enrichments.append(
                CreateEnrichmentParameters(
                    description=description,
                    format=format_type,
                )
            )

        print(f"Creating Webset with query: {search_query}")
        print(f"Enrichments: {', '.join(enrichment_list)}")

        # Create a Webset with search parameters and enrichments
        webset = exa_client.websets.create(
            params=CreateWebsetParameters(
                search={
                    "query": search_query,
                    "count": search_limit
                },
                enrichments=enrichments,
            )
        )

        print(f"Webset created with ID: {webset.id}")
        return webset
    except Exception as e:
        print(f"Error creating Webset: {e}")
        return None

def wait_for_webset_processing(exa_client: Exa, webset_id: str, timeout: int = TIMEOUT) -> Optional[Dict[str, Any]]:
    """
    Wait for a Webset to finish processing.

    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to wait for
        timeout: Maximum time to wait in seconds

    Returns:
        Dict: Updated Webset object or None if waiting fails
    """
    try:
        print("Waiting for Webset to process...")
        start_time = time.time()

        # Poll for Webset status until it's idle or timeout is reached
        while True:
            webset = exa_client.websets.get(webset_id)

            if webset.status == "idle":
                print("Webset processing complete!")
                return webset

            # Check if timeout has been reached
            if time.time() - start_time > timeout:
                print(f"Timeout reached after {timeout} seconds. Current status: {webset.status}")
                return webset

            # Wait before polling again
            print(f"Current status: {webset.status}... (waiting)")
            time.sleep(10)  # Poll every 10 seconds
    except Exception as e:
        print(f"Error waiting for Webset: {e}")
        return None

def fetch_webset_items(exa_client: Exa, webset_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch items from a Webset.

    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to fetch items from

    Returns:
        List: List of Webset items or None if fetching fails
    """
    try:
        # Retrieve Webset Items
        items_response = exa_client.websets.items.list(webset_id=webset_id)

        if not items_response.data:
            print("No items found in the Webset.")
            return []

        print(f"Found {len(items_response.data)} items in the Webset.")
        return items_response.data
    except Exception as e:
        print(f"Error fetching Webset items: {e}")
        return None

def format_and_save_results(items: List[Dict[str, Any]], config: Dict[str, Any], output_file: Optional[str] = None) -> None:
    """
    Format and save Webset items with specific fields.

    Args:
        items: List of Webset items to format
        config: Configuration data
        output_file: Optional file path to save results to
    """
    if not items:
        print("No items to format.")
        return

    # Prepare formatted results
    formatted_results = []

    for item in items:
        try:
            # Extract basic item information
            result = {
                "id": item.id,
                "source": item.source,
                "webset_id": item.webset_id
            }

            # Extract properties based on item type
            if hasattr(item, "properties"):
                properties = item.properties
                if hasattr(properties, "name"):
                    result["name"] = properties.name
                if hasattr(properties, "url"):
                    result["url"] = properties.url

            # Extract enrichments
            if hasattr(item, "enrichments") and item.enrichments:
                enrichments = {}
                # Map enrichment IDs to field names
                enrichment_id_to_field = {
                    "wenrich_cmaqsapcr00crl00itj2ihcx4": "Name",
                    "wenrich_cmaqsapcr00csl00iv9o50m44": "Email",
                    "wenrich_cmaqsapcr00ctl00iq4gpyqo6": "Phone",
                    "wenrich_cmaqsapcr00cul00i3l2dfhq7": "Location",
                    "wenrich_cmaqsapcr00cvl00i5p9iokr4": "Company Name",
                    "wenrich_cmaqsapcr00cwl00ij7q5v78o": "Company Website"
                }

                for enrichment in item.enrichments:
                    # Get the enrichment ID and result
                    enrichment_id = getattr(enrichment, "enrichment_id", "")
                    result_value = enrichment.result

                    # Skip if no result
                    if not result_value:
                        continue

                    # Convert list result to string
                    if isinstance(result_value, list) and result_value:
                        result_value = result_value[0]

                    # Try to determine the field from the enrichment ID
                    if enrichment_id in enrichment_id_to_field:
                        field = enrichment_id_to_field[enrichment_id]
                        enrichments[field] = result_value
                        continue

                    # If no match from ID, try to determine from the format
                    enrichment_format = getattr(enrichment, "format", "text")
                    if enrichment_format == "email":
                        enrichments["Email"] = result_value
                    elif enrichment_format == "phone":
                        enrichments["Phone"] = result_value
                    else:
                        # Try to determine from the result content
                        result_str = str(result_value).lower()
                        if "@" in result_str and "." in result_str:
                            enrichments["Email"] = result_value
                        elif "http" in result_str or ".com" in result_str or ".org" in result_str:
                            enrichments["Company Website"] = result_value
                        elif any(state in result_str for state in ["california", "los angeles", "san francisco"]):
                            enrichments["Location"] = result_value
                result["enrichments"] = enrichments

            # Add to formatted results
            formatted_results.append(result)
        except Exception as e:
            print(f"Error formatting item {item.id}: {e}")

    # Print formatted results
    print("\n" + "="*80)
    print(f"FORMATTED RESULTS ({len(formatted_results)} items)")
    print("="*80)

    for i, result in enumerate(formatted_results, 1):
        print(f"\nRESULT {i}:")

        # Print basic information
        if "name" in result:
            print(f"Name: {result['name']}")
        if "url" in result:
            print(f"URL: {result['url']}")

        # Print enrichments
        if "enrichments" in result:
            print("\nEnrichments:")
            for field, value in result["enrichments"].items():
                print(f"  {field}: {value}")

        print("-"*80)

    # Save to file if requested
    if output_file:
        try:
            # Convert any URL objects to strings
            json_results = []
            for result in formatted_results:
                json_result = {}
                for key, value in result.items():
                    if key == "url" and hasattr(value, "__str__"):
                        json_result[key] = str(value)
                    elif key == "enrichments":
                        json_result[key] = {}
                        for field, field_value in value.items():
                            if hasattr(field_value, "__str__"):
                                json_result[key][field] = str(field_value)
                            else:
                                json_result[key][field] = field_value
                    else:
                        json_result[key] = value
                json_results.append(json_result)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"results": json_results}, f, indent=2)
            print(f"\nResults saved to {output_file}")
        except Exception as e:
            print(f"Error saving results to file: {e}")

def main():
    """Main function to execute the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch and display Exa Websets data")
    parser.add_argument("--config", type=str, default="../config/config.json", help="Path to configuration file")
    parser.add_argument("--output", "-o", type=str, default="../results/webset_results.json", help="Output file to save results to")
    parser.add_argument("--webset-id", type=str, help="Use existing Webset ID instead of creating a new one")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up Exa client
    exa_client = setup_exa_client()
    if not exa_client:
        sys.exit(1)

    # Use existing Webset or create a new one
    if args.webset_id:
        print(f"Using existing Webset with ID: {args.webset_id}")
        webset_id = args.webset_id
    else:
        # Create a new Webset
        webset = create_webset(exa_client, config)
        if not webset:
            sys.exit(1)
        webset_id = webset.id

    # Wait for Webset processing
    webset = wait_for_webset_processing(exa_client, webset_id)
    if not webset:
        sys.exit(1)

    # Fetch Webset items
    items = fetch_webset_items(exa_client, webset_id)
    if items is None:
        sys.exit(1)

    # Format and save results
    format_and_save_results(items, config, args.output)

if __name__ == "__main__":
    main()
