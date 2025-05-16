#!/usr/bin/env python3
import requests
import os
from bs4 import BeautifulSoup

# List of URLs to fetch
urls = [
    "https://docs.exa.ai/websets/api/websets/create-a-webset.md",
    "https://docs.exa.ai/websets/api/websets/get-a-webset.md",
    "https://docs.exa.ai/websets/api/websets/update-a-webset.md",
    "https://docs.exa.ai/websets/api/websets/delete-a-webset.md",
    "https://docs.exa.ai/websets/api/websets/cancel-a-running-webset.md",
    "https://docs.exa.ai/websets/api/websets/list-all-websets.md",
    "https://docs.exa.ai/websets/api/get-started.md",
    "https://docs.exa.ai/websets/api/overview.md"
]

# Output file
output_file = "documentation.md"

def fetch_content(url):
    """Fetch content from a URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if the URL ends with .md, which means we're directly fetching a markdown file
        if url.endswith('.md'):
            return response.text
        else:
            # If it's an HTML page, parse it to extract the markdown content
            soup = BeautifulSoup(response.text, 'html.parser')
            # This is a simplistic approach - you might need to adjust based on the actual structure
            content = soup.find('article') or soup.find('main') or soup.find('body')
            return content.get_text() if content else response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return f"# Error fetching content from {url}\n\n{str(e)}\n\n"

def main():
    """Main function to fetch all content and write to file"""
    all_content = []
    
    print("Fetching content from URLs...")
    for url in urls:
        print(f"Processing: {url}")
        content = fetch_content(url)
        
        # Add a header with the source URL
        url_header = f"\n\n## Source: {url}\n\n"
        all_content.append(url_header + content)
    
    # Write all content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Exa.ai Websets API Documentation\n\n")
        f.write("*This document is a compilation of documentation from various Exa.ai Websets API pages.*\n\n")
        f.write("".join(all_content))
    
    print(f"\nDocumentation compiled successfully to {output_file}")

if __name__ == "__main__":
    main()
