#!/usr/bin/env python3
"""
Exa Websets API Client

This script uses the Exa Websets API to fetch and display specific details from websets.
It demonstrates how to authenticate, make API calls, and process the results.
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from exa_py import Exa
from exa_py.websets.types import CreateWebsetParameters, CreateEnrichmentParameters

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
API_KEY = os.getenv('exa_api_key')
if not API_KEY:
    print("Error: API key not found. Please set 'exa_api_key' in your .env file.")
    sys.exit(1)

# Initialize Exa client
exa = Exa(API_KEY)

def create_webset(query: str, count: int = 3) -> Dict[str, Any]:
    """
    Create a new webset with the specified query and item count.
    
    Args:
        query: The search query to use for finding items
        count: Maximum number of items to retrieve (default: 3)
        
    Returns:
        The created webset object
    """
    try:
        print(f"Creating webset with query: '{query}' (max {count} items)...")
        
        webset = exa.websets.create(
            params=CreateWebsetParameters(
                search={
                    "query": query,
                    "count": count
                },
                # Optional: Add enrichments if needed
                # enrichments=[
                #     CreateEnrichmentParameters(
                #         description="Company founding year",
                #         format="number",
                #     ),
                # ],
            )
        )
        
        print(f"Webset created successfully with ID: {webset.id}")
        return webset
    except Exception as e:
        print(f"Error creating webset: {e}")
        sys.exit(1)

def wait_for_webset_completion(webset_id: str, timeout_seconds: int = 120) -> Dict[str, Any]:
    """
    Wait for a webset to complete processing.
    
    Args:
        webset_id: The ID of the webset to wait for
        timeout_seconds: Maximum time to wait in seconds
        
    Returns:
        The completed webset object
    """
    print(f"Waiting for webset {webset_id} to complete processing...")
    
    try:
        # Use the built-in wait_until_idle method with a timeout
        webset = exa.websets.wait_until_idle(
            webset_id, 
            timeout=timeout_seconds * 1000,
            poll_interval=2000
        )
        print(f"Webset processing completed with status: {webset.status}")
        return webset
    except Exception as e:
        print(f"Error or timeout waiting for webset: {e}")
        # Try to get the current state anyway
        return exa.websets.get(webset_id)

def get_webset_items(webset_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all items from a webset.
    
    Args:
        webset_id: The ID of the webset to get items from
        
    Returns:
        List of webset items
    """
    try:
        print(f"Retrieving items from webset {webset_id}...")
        items_response = exa.websets.items.list(webset_id=webset_id)
        items = items_response.data
        print(f"Retrieved {len(items)} items")
        return items
    except Exception as e:
        print(f"Error retrieving webset items: {e}")
        return []

def display_webset_items(items: List[Dict[str, Any]], output_file: str = "exa_results.json") -> None:
    """
    Display formatted information about webset items and save to a file.
    
    Args:
        items: List of webset items to display
        output_file: File path to save the results (default: exa_results.json)
    """
    import json
    
    if not items:
        print("No items found in the webset.")
        with open(output_file, 'w') as f:
            json.dump({"message": "No items found in the webset."}, f, indent=2)
        print(f"Empty result saved to {output_file}")
        return
    
    print("\n===== WEBSET ITEMS =====\n")
    
    # Prepare data for both display and saving
    results = []
    
    for i, item in enumerate(items, 1):
        print(f"ITEM {i}:")
        item_data = {"item_number": i}
        
        # Extract properties based on the entity type
        properties = item.properties
        entity_type = properties.type
        
        # Display and store common properties
        print(f"  URL: {properties.url}")
        print(f"  Type: {entity_type}")
        print(f"  Description: {properties.description}")
        
        item_data.update({
            "url": properties.url,
            "type": entity_type,
            "description": properties.description
        })
        
        # Display and store entity-specific properties
        entity_data = {}
        if entity_type == "company":
            company = properties.company
            print(f"  Company Name: {company.name}")
            entity_data["name"] = company.name
            
            if company.location:
                print(f"  Location: {company.location}")
                entity_data["location"] = company.location
                
            if company.industry:
                print(f"  Industry: {company.industry}")
                entity_data["industry"] = company.industry
                
            if company.about:
                print(f"  About: {company.about}")
                entity_data["about"] = company.about
                
            if company.employees:
                print(f"  Employees: {company.employees}")
                entity_data["employees"] = company.employees
            
        elif entity_type == "person":
            person = properties.person
            print(f"  Name: {person.name}")
            entity_data["name"] = person.name
            
            if person.position:
                print(f"  Position: {person.position}")
                entity_data["position"] = person.position
                
            if person.location:
                print(f"  Location: {person.location}")
                entity_data["location"] = person.location
                
        elif entity_type == "article" or entity_type == "research_paper":
            article = getattr(properties, entity_type)
            if article.author:
                print(f"  Author: {article.author}")
                entity_data["author"] = article.author
                
            if article.publishedAt:
                print(f"  Published: {article.publishedAt}")
                entity_data["published_at"] = article.publishedAt
        
        item_data[entity_type] = entity_data
                
        # Display and store evaluations
        if item.evaluations:
            print("\n  Evaluations:")
            evaluations = []
            for eval in item.evaluations:
                print(f"    • {eval.criterion}: {eval.satisfied}")
                evaluations.append({
                    "criterion": eval.criterion,
                    "satisfied": eval.satisfied,
                    "reasoning": eval.reasoning
                })
            item_data["evaluations"] = evaluations
        
        # Display and store enrichments if available
        if item.enrichments:
            print("\n  Enrichments:")
            enrichments = []
            for enrich in item.enrichments:
                result_text = ", ".join(enrich.result) if enrich.result else "N/A"
                print(f"    • {enrich.format}: {result_text}")
                enrichments.append({
                    "format": enrich.format,
                    "result": enrich.result
                })
            item_data["enrichments"] = enrichments
        
        results.append(item_data)
        print("\n" + "-" * 50 + "\n")
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump({"results": results}, f, indent=2)
    
    print(f"Results saved to {output_file}")

def main():
    """Main function to execute the script."""
    try:
        # Create a new webset with a sample query
        query = "Top AI research labs focusing on large language models"
        webset = create_webset(query, count=3)
        
        # Wait for the webset to complete processing
        webset = wait_for_webset_completion(webset.id)
        
        # Get and display the webset items
        items = get_webset_items(webset.id)
        display_webset_items(items)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
