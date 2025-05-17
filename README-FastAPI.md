# Exa API FastAPI Application

This is a FastAPI application that provides a RESTful API for interacting with the Exa Search and Websets APIs. It converts the existing Python scripts (`exa_search.py`, `exa_websets.py`, `check_webset.py`) into a structured FastAPI application.

## Features

- RESTful API endpoints for searching, creating websets, and checking webset status
- Async/await patterns for all I/O operations
- Proper error handling with appropriate HTTP status codes
- Pydantic models for request/response validation
- API documentation using FastAPI's built-in Swagger UI
- Environment variable handling for the Exa API key

## Project Structure

```
app/
├── api/
│   ├── routes/
│   │   ├── search.py
│   │   └── websets.py
│   ├── schemas/
│   │   ├── search.py
│   │   └── websets.py
│   ├── services/
│   │   ├── search_service.py
│   │   └── webset_service.py
│   └── utils/
│       ├── dependencies.py
│       └── errors.py
├── tests/
│   ├── test_search.py
│   └── test_websets.py
└── main.py
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/exa-api.git
   cd exa-api
   ```

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

## Running the FastAPI Server

1. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

2. The API will be available at http://localhost:8000

3. API documentation is available at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Search API

- `POST /api/search/`: Perform a search using the Exa Search API

### Websets API

- `POST /api/websets/`: Create a new Webset
- `GET /api/websets/{webset_id}`: Get the status of a Webset
- `GET /api/websets/{webset_id}/wait`: Wait for a Webset to finish processing
- `GET /api/websets/{webset_id}/items`: Fetch items from a Webset
- `GET /api/websets/{webset_id}/formatted`: Fetch and format items from a Webset

## Running Tests

Run the tests using pytest:

```
pytest app/tests/
```

## Example Usage

### Search API

```bash
curl -X 'POST' \
  'http://localhost:8000/api/search/' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Top AI research labs focusing on large language models",
  "num_results": 3,
  "use_autoprompt": true
}'
```

### Websets API

Create a new Webset:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/websets/' \
  -H 'Content-Type: application/json' \
  -d '{
  "search": {
    "query": "entrepreneur (founder, co-founder, or owner of a business) currently resides in the usa",
    "count": 3
  },
  "enrichments": [
    {
      "description": "Extract the full name of the entrepreneur (founder, co-founder, or business owner)",
      "format": "text"
    },
    {
      "description": "Extract the email address of the entrepreneur for contact purposes",
      "format": "email"
    }
  ]
}'
```

Get Webset status:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/websets/webset_cmaqrbpy900b5mk0ialbn5z07'
```

Get formatted Webset items:

```bash
curl -X 'GET' \
  'http://localhost:8000/api/websets/webset_cmaqrbpy900b5mk0ialbn5z07/formatted'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
