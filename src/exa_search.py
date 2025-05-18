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

import argparse
import json
import os
import sys
import time

from dotenv import load_dotenv
from exa_py import Exa
from exa_py.websets.types import (
    CreateEnrichmentParameters,
    CreateWebsetParameters,
    WebsetWebhookParameters,
)

from src.utils.excel_export import json_to_excel

# Default timeout for waiting for Webset processing (in seconds)
TIMEOUT = 300  # 5 minutes


def load_config(config_file: str) -> dict:
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        print(f"Configuration loaded from {config_file}")
        return cfg
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def setup_exa_client() -> Exa:
    load_dotenv()
    api_key = os.getenv("exa_api_key")
    if not api_key:
        print("Error: No API key found. Please set 'exa_api_key' in your .env file.")
        sys.exit(1)
    try:
        client = Exa(api_key)
        print(f"Exa client initialized with API key: {api_key[:4]}...{api_key[-4:]}")
        return client
    except Exception as e:
        print(f"Error initializing Exa client: {e}")
        sys.exit(1)


def create_webset(exa_client: Exa, cfg: dict) -> str:
    query = cfg["search"]["query"]
    count = cfg["search"].get("count", cfg["search"].get("limit", 10))
    entity_type = cfg["search"].get("entityType", "person")
    external_id = cfg.get("externalId")
    metadata = cfg.get("metadata", {})

    enrichments = []
    for field in cfg.get("enrichments", []):
        fmt = "text"
        if field.lower() == "email":
            fmt = "email"
        elif field.lower() == "phone":
            fmt = "phone"
        description = f"Extract the {field} of the entrepreneur"
        enrichments.append(CreateEnrichmentParameters(description=description, format=fmt))

    params = CreateWebsetParameters(
        search={"query": query, "count": count, "entity": {"type": entity_type}},
        enrichments=enrichments,
        externalId=external_id,
        metadata=metadata,
    )

    webset = exa_client.websets.create(params=params)
    print(f"Webset created with ID: {webset.id}")
    return webset.id


def register_webhook(exa_client: Exa, webset_id: str, webhook_url: str) -> None:
    params = WebsetWebhookParameters(websetId=webset_id, url=webhook_url, events=["item.created", "item.enriched"])
    hook = exa_client.websets.webhooks.create(params=params)
    print(f"Webhook created with ID: {hook.id} → {webhook_url}")


def wait_for_webset_processing(exa_client: Exa, webset_id: str, timeout: int = TIMEOUT):
    print("Waiting for webset processing...")
    start = time.time()
    while True:
        webset = exa_client.websets.get(webset_id)
        if webset.status == "idle":
            print("Webset processing complete")
            return webset
        if time.time() - start > timeout:
            print(f"Timeout after {timeout}s. Status: {webset.status}")
            return webset
        print(f"Current status: {webset.status}. Waiting...")
        time.sleep(10)


def fetch_webset_items(exa_client: Exa, webset_id: str):
    items_response = exa_client.websets.items.list(webset_id=webset_id)
    items = items_response.data or []
    print(f"Fetched {len(items)} items")
    return items


def format_and_save_results(items: list, output_file: str = None):
    formatted = []
    for item in items:
        try:
            res = {"id": item.id, "source": item.source, "webset_id": item.webset_id}
            props = getattr(item, "properties", None)
            if props:
                if hasattr(props, "name"):
                    res["name"] = props.name
                if hasattr(props, "url"):
                    res["url"] = str(props.url)

            enrich = {}
            for enr in getattr(item, "enrichments", []):
                val = enr.result
                if not val:
                    continue
                if isinstance(val, list) and val:
                    val = val[0]
                fmt = getattr(enr, "format", "text")
                if fmt == "email":
                    enrich["Email"] = val
                elif fmt == "phone":
                    enrich["Phone"] = val
                else:
                    text = str(val)
                    if "@" in text and "." in text:
                        enrich["Email"] = text
                    elif text.startswith("http"):
                        enrich["Company Website"] = text
                    else:
                        field = enr.description.split("Extract the ")[-1].split(" ")[0]
                        enrich[field] = text
            if enrich:
                res["enrichments"] = enrich
            formatted.append(res)
        except Exception as e:
            print(f"Error formatting item {item.id}: {e}")

    for i, res in enumerate(formatted, 1):
        print(f"\nResult {i}:")
        for k, v in res.items():
            print(f"{k}: {v}")

    if output_file:
        data = {"results": formatted}
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {output_file}")
        try:
            excel_file = json_to_excel(data, output_file)
            print(f"Also saved as Excel: {excel_file}")
        except Exception as e:
            print(f"Excel export failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Exa Websets ICA script")
    parser.add_argument("--config", "-c", default="config.json")
    parser.add_argument("--output", "-o", default="results.json")
    parser.add_argument("--webset-id", help="Use existing webset ID")
    parser.add_argument("--webhook-url", "-w", help="Webhook endpoint URL")
    args = parser.parse_args()

    cfg = load_config(args.config)
    exa_client = setup_exa_client()

    if args.webset_id:
        webset_id = args.webset_id
        print(f"Using existing webset ID: {webset_id}")
    else:
        webset_id = create_webset(exa_client, cfg)

    if args.webhook_url:
        register_webhook(exa_client, webset_id, args.webhook_url)

    wait_for_webset_processing(exa_client, webset_id)
    items = fetch_webset_items(exa_client, webset_id)
    format_and_save_results(items, args.output)


if __name__ == "__main__":
    main()
