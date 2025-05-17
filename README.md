# Exa API Scripts

This repository contains scripts for working with the Exa API to search for information and process the results. It includes scripts for both the Exa Search API and the Exa Websets API.

## Project Structure

- `src/` - Python source code files
  - `utils/` - Utility modules including Excel export functionality
- `config/` - Configuration files
- `results/` - Output files and results (JSON, text, and Excel formats)
- `tests/` - Test files for the codebase
- `documentation.md` - Detailed API documentation
- `README.md` - This file

## Scripts

### 1. src/exa_websets.py

This script creates a new Webset with the specified search criteria and enrichments, waits for it to process, and then retrieves and formats the results.

#### Usage

```bash
python src/exa_websets.py [--config config/config.json] [--output results/webset_results.json] [--webset-id WEBSET_ID]
```

Options:
- `--config`: Path to the configuration file (default: config/config.json)
- `--output`: Output file to save results to (default: results/webset_results.json)
- `--webset-id`: Use an existing Webset ID instead of creating a new one

### 2. src/check_webset.py

This script checks the status of an existing Webset and retrieves its items if the Webset is idle.

#### Usage

```bash
python src/check_webset.py --webset-id WEBSET_ID [--output results/webset_check_results.json] [--raw]
```

Options:
- `--webset-id`: ID of the Webset to check (required)
- `--config`: Path to the configuration file (default: config/config.json)
- `--output`: Output file to save results to (default: results/webset_check_results.json)
- `--raw`: Inspect and save raw item data

### 3. src/exa_search.py

This script uses the Exa Search API to search for information and display the results in a formatted way.

## Features

- Authenticate with the Exa API using an API key from a `.env` file
- Perform searches with customizable queries
- Limit the number of results displayed
- Format and display search results with relevant metadata
- Save results to both JSON/text and Excel/Google Sheets formats
- Handle missing fields gracefully by keeping them blank in the output

## Requirements

- Python 3.6+
- `exa-py` Python package
- `python-dotenv` package
- `pandas` package for data manipulation
- `openpyxl` package for Excel file generation

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the root directory with your Exa API key:
   ```
   exa_api_key=your_api_key_here
   ```

## Usage

### src/exa_search.py

Basic usage:
```
python src/exa_search.py
```

This will perform a search using the default query: "Top AI research labs focusing on large language models"

Command-line Options:
- `--query "Your search query"`: Specify a custom search query
- `--output filename.txt` or `-o filename.txt`: Save the results to a file (default: results/search_results.txt)
- `--limit N` or `-l N`: Limit the number of results (default: 3)

Examples:
```
# Custom search query
python src/exa_search.py --query "Best machine learning frameworks 2025"

# Save results to a file
python src/exa_search.py --output results/custom_search_results.txt

# Limit to 5 results
python src/exa_search.py --limit 5

# Combine options
python src/exa_search.py --query "AI startups in healthcare" --output results/healthcare_ai.txt --limit 10
```

### src/exa_websets.py

Basic usage:
```
python src/exa_websets.py
```

This will create a new Webset with the search criteria and enrichments specified in config/config.json.

Examples:
```
# Use an existing Webset
python src/exa_websets.py --webset-id webset_cmaqrbpy900b5mk0ialbn5z07

# Save results to a file
python src/exa_websets.py --output results/entrepreneur_results.json

# Use a custom config file
python src/exa_websets.py --config config/custom_config.json
```

### src/check_webset.py

Basic usage:
```
python src/check_webset.py --webset-id webset_cmaqrbpy900b5mk0ialbn5z07
```

Examples:
```
# Save results to a file
python src/check_webset.py --webset-id webset_cmaqrbpy900b5mk0ialbn5z07 --output results/webset_check_results.json

# Inspect raw item data
python src/check_webset.py --webset-id webset_cmaqrbpy900b5mk0ialbn5z07 --raw
```

## Output Format

### src/exa_search.py

The script displays search results with the following information (when available):

- Title
- URL
- Publication date
- Author
- Source
- Relevance score
- Text excerpt

Results are saved in two formats:
1. Text file (.txt) - Human-readable formatted text
2. Excel file (.xlsx) - Tabular data for analysis and processing

### src/exa_websets.py and src/check_webset.py

These scripts generate output in two formats:

1. JSON format with the following structure:

```json
{
  "results": [
    {
      "id": "witem_01jvcg32bdreggpdvrreggpdvr",
      "source": "search",
      "webset_id": "webset_cmaqrbpy900b5mk0ialbn5z07",
      "url": "https://www.linkedin.com/in/negocios-latinos",
      "enrichments": {
        "Phone": [
          "+13127020116"
        ],
        "Location": [
          "Greater Chicago Area, US"
        ],
        "Company Name": [
          "Linea411"
        ]
      }
    }
  ]
}
```

2. Excel format (.xlsx) - Tabular data with the same information, suitable for analysis and processing in spreadsheet applications. Missing fields are kept blank rather than filled with null values.

## Configuration

The Websets scripts use a configuration file (`config/config.json`) to specify search criteria and enrichments:

```json
{
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
```

## Error Handling

The scripts include error handling for:
- Missing API key
- API authentication issues
- Search failures
- Result processing errors
- File saving errors

## Notes

- The Exa Websets API is asynchronous, so it may take some time for a Webset to process.
- The enrichments may not always be able to extract all requested information for every result.

## Running Tests

The project includes tests to verify the functionality of the Excel export feature and integration with the main scripts. To run the tests:

```bash
pytest tests/
```

Or run specific test files:

```bash
pytest tests/test_excel_export.py
pytest tests/test_integration.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
