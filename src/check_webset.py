#!/usr/bin/env python3
"""
Exa Webset Status Checker

This script checks the status of an existing Exa Webset and retrieves its items
if the Webset is idle.

Usage:
    python check_webset.py --webset-id WEBSET_ID [--output OUTPUT_FILE]
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from exa_py import Exa

from src.utils.excel_export import json_to_excel


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        config_file: Path to the configuration file

    Returns:
        Dict: Configuration data
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"Configuration loaded from {config_file}")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration")
        return {
            "enrichments": [
                "Name",
                "Email",
                "Phone",
                "Location",
                "Company Name",
                "Company Website",
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
    api_key = os.getenv("exa_api_key")

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


def check_webset_status(exa_client: Exa, webset_id: str) -> Optional[Dict[str, Any]]:
    """
    Check the status of a Webset.

    Args:
        exa_client: Authenticated Exa client
        webset_id: ID of the Webset to check

    Returns:
        Dict: Webset object or None if checking fails
    """
    try:
        webset = exa_client.websets.get(webset_id)
        print(f"Webset status: {webset.status}")
        return webset
    except Exception as e:
        print(f"Error checking Webset status: {e}")
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


def format_and_save_results(
    items: List[Dict[str, Any]],
    config: Dict[str, Any],
    output_file: Optional[str] = None,
) -> None:
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
                "webset_id": item.webset_id,
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

                # Print enrichment structure for debugging
                print(f"\nEnrichment structure for item {item.id}:")
                for i, enrichment in enumerate(item.enrichments):
                    print(f"  Enrichment {i+1}:")
                    for attr in [
                        "enrichment_id",
                        "format",
                        "result",
                        "reasoning",
                        "references",
                    ]:
                        if hasattr(enrichment, attr):
                            value = getattr(enrichment, attr)
                            if attr == "result" and isinstance(value, list) and value:
                                value = value[0]  # Show just the first item if it's a list
                            print(f"    {attr}: {value}")

                # Map enrichment IDs to field names
                enrichment_id_to_field = {
                    "wenrich_cmaqsapcr00crl00itj2ihcx4": "Name",
                    "wenrich_cmaqsapcr00csl00iv9o50m44": "Email",
                    "wenrich_cmaqsapcr00ctl00iq4gpyqo6": "Phone",
                    "wenrich_cmaqsapcr00cul00i3l2dfhq7": "Location",
                    "wenrich_cmaqsapcr00cvl00i5p9iokr4": "Company Name",
                    "wenrich_cmaqsapcr00cwl00ij7q5v78o": "Company Website",
                }

                # Map formats to field names as fallback
                format_to_field = {
                    "email": "Email",
                    "phone": "Phone",
                }

                # Get the list of enrichment fields from config
                enrichment_fields = config.get("enrichments", [])

                # Process each enrichment
                for enrichment in item.enrichments:
                    # Skip if no result
                    if not hasattr(enrichment, "result") or enrichment.result is None:
                        continue

                    # Get the enrichment format and ID
                    enrichment_format = getattr(enrichment, "format", "text")
                    enrichment_id = getattr(enrichment, "enrichment_id", "")

                    # Get the result (could be a string or a list)
                    result_value = enrichment.result
                    if isinstance(result_value, list):
                        result_value = result_value[0] if result_value else ""

                    # Convert to string for pattern matching
                    result_str = str(result_value).lower()

                    # Try to determine the field type based on the enrichment ID (most reliable)
                    if enrichment_id in enrichment_id_to_field:
                        field_name = enrichment_id_to_field[enrichment_id]
                        enrichments[field_name] = result_value
                        continue

                    # Try to determine the field type based on the format
                    if enrichment_format in format_to_field:
                        field_name = format_to_field[enrichment_format]
                        enrichments[field_name] = result_value
                        continue

                    # If format is text, try to determine the field type based on the content and reasoning
                    if enrichment_format == "text":
                        # Get the reasoning if available
                        reasoning = getattr(enrichment, "reasoning", "")

                        # Check reasoning for clues about the field type
                        if reasoning:
                            if "name" in reasoning.lower() and "entrepreneur" in reasoning.lower():
                                enrichments["Name"] = result_value
                            elif "location" in reasoning.lower() or "resides" in reasoning.lower():
                                enrichments["Location"] = result_value
                            elif (
                                "company" in reasoning.lower()
                                or "business" in reasoning.lower()
                                or "owner" in reasoning.lower()
                            ):
                                enrichments["Company Name"] = result_value
                            elif "website" in reasoning.lower() or "url" in reasoning.lower():
                                enrichments["Company Website"] = result_value
                            # Try to match by looking for field names in the reasoning
                            else:
                                for field in enrichment_fields:
                                    if field.lower() in reasoning.lower():
                                        enrichments[field] = result_value
                                        break

                        # If no match from reasoning, try to determine from the result content
                        matched = False
                        for field in enrichment_fields:
                            if field in enrichments:
                                matched = True
                                break

                        if not matched:
                            if "@" in result_str and "." in result_str:
                                enrichments["Email"] = result_value
                            elif "http" in result_str or ".com" in result_str or ".org" in result_str:
                                enrichments["Company Website"] = result_value
                            elif any(
                                state in result_str
                                for state in [
                                    "alabama",
                                    "alaska",
                                    "arizona",
                                    "california",
                                    "colorado",
                                    "florida",
                                    "georgia",
                                    "illinois",
                                    "new york",
                                    "texas",
                                    "washington",
                                    "united states",
                                    "usa",
                                ]
                            ):
                                enrichments["Location"] = result_value
                            elif any(char.isdigit() for char in result_str) and (
                                "-" in result_str or "(" in result_str or ")" in result_str
                            ):
                                enrichments["Phone"] = result_value
                            # Check if it looks like a name (capitalized words)
                            elif all(word[0].isupper() for word in result_value.split() if word):
                                enrichments["Name"] = result_value
                            # Check if it looks like a company name (often has Inc, LLC, etc.)
                            elif any(
                                term in result_str
                                for term in [
                                    "inc",
                                    "llc",
                                    "corp",
                                    "company",
                                    "technologies",
                                    "solutions",
                                ]
                            ):
                                enrichments["Company Name"] = result_value

                result["enrichments"] = enrichments

            # Add to formatted results
            formatted_results.append(result)
        except Exception as e:
            print(f"Error formatting item {item.id}: {e}")

    # Print formatted results
    print("\n" + "=" * 80)
    print(f"FORMATTED RESULTS ({len(formatted_results)} items)")
    print("=" * 80)

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

        print("-" * 80)

    # Save to file if requested
    if output_file:
        try:
            # Use a custom JSON encoder to handle non-serializable objects
            class CustomEncoder(json.JSONEncoder):
                def default(self, obj):
                    try:
                        return str(obj)
                    except:
                        return "Non-serializable object"

            # Save to JSON file
            json_data = {"results": formatted_results}
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, cls=CustomEncoder)
            print(f"\nResults saved to {output_file}")

            # Save to Excel file
            try:
                excel_file = json_to_excel(json_data, output_file)
                if excel_file:
                    print(f"Results also saved to Excel file: {excel_file}")
            except Exception as e:
                print(f"Error saving results to Excel file: {e}")
        except Exception as e:
            print(f"Error saving results to file: {e}")


def inspect_raw_items(items: List[Dict[str, Any]], output_file: Optional[str] = None) -> None:
    """
    Inspect and save the raw structure of Webset items.

    Args:
        items: List of Webset items to inspect
        output_file: Optional file path to save raw data to
    """
    if not items:
        print("No items to inspect.")
        return

    print("\n" + "=" * 80)
    print(f"RAW ITEM INSPECTION ({len(items)} items)")
    print("=" * 80)

    raw_data = []

    for i, item in enumerate(items, 1):
        print(f"\nITEM {i} ID: {item.id}")

        # Collect available attributes
        attributes = dir(item)
        print(f"Available attributes: {', '.join(attr for attr in attributes if not attr.startswith('_'))}")

        # Inspect enrichments if available
        if hasattr(item, "enrichments") and item.enrichments:
            print(f"Number of enrichments: {len(item.enrichments)}")

            for j, enrichment in enumerate(item.enrichments, 1):
                print(f"  Enrichment {j}:")
                enrichment_attrs = dir(enrichment)
                print(
                    f"  Available attributes: {', '.join(attr for attr in enrichment_attrs if not attr.startswith('_'))}"
                )

                # Print enrichment details
                if hasattr(enrichment, "result"):
                    print(f"  Result: {enrichment.result}")

                # Try to convert to dict for raw data
                try:
                    enrichment_dict = {
                        attr: getattr(enrichment, attr)
                        for attr in enrichment_attrs
                        if not attr.startswith("_") and not callable(getattr(enrichment, attr))
                    }
                    print(f"  Data: {enrichment_dict}")
                except Exception as e:
                    print(f"  Error converting to dict: {e}")

        # Try to convert item to dict for raw data
        try:
            item_dict = {}
            for attr in attributes:
                if not attr.startswith("_") and not callable(getattr(item, attr)):
                    value = getattr(item, attr)
                    if attr == "enrichments":
                        # Handle enrichments separately
                        item_dict[attr] = [
                            {a: getattr(e, a) for a in dir(e) if not a.startswith("_") and not callable(getattr(e, a))}
                            for e in value
                        ]
                    else:
                        item_dict[attr] = value
            raw_data.append(item_dict)
        except Exception as e:
            print(f"Error converting item to dict: {e}")

    # Save raw data to file if requested
    if output_file:
        try:
            # Extract filename from path
            output_filename = os.path.basename(output_file)
            raw_output_file = f"../results/raw_{output_filename}"
            with open(raw_output_file, "w", encoding="utf-8") as f:
                # Use a custom JSON encoder to handle non-serializable objects
                class CustomEncoder(json.JSONEncoder):
                    def default(self, obj):
                        try:
                            return str(obj)
                        except:
                            return "Non-serializable object"

                json.dump(raw_data, f, indent=2, cls=CustomEncoder)
            print(f"\nRaw data saved to {raw_output_file}")
        except Exception as e:
            print(f"Error saving raw data to file: {e}")


def main():
    """Main function to execute the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Check Exa Webset status and retrieve items")
    parser.add_argument("--webset-id", required=True, help="ID of the Webset to check")
    parser.add_argument(
        "--config",
        type=str,
        default="../config/config.json",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="../results/webset_check_results.json",
        help="Output file to save results to",
    )
    parser.add_argument("--raw", action="store_true", help="Inspect and save raw item data")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Set up Exa client
    exa_client = setup_exa_client()
    if not exa_client:
        sys.exit(1)

    # Check Webset status
    webset = check_webset_status(exa_client, args.webset_id)
    if not webset:
        sys.exit(1)

    # If Webset is idle, fetch and format items
    if webset.status == "idle":
        items = fetch_webset_items(exa_client, args.webset_id)
        if items is None:
            sys.exit(1)

        # Inspect raw items if requested
        if args.raw:
            inspect_raw_items(items, args.output)

        # Format and save results
        format_and_save_results(items, config, args.output)
    else:
        print(f"Webset is not idle (current status: {webset.status}). Please check again later.")


if __name__ == "__main__":
    main()
