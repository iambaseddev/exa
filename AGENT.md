# Agent Guidelines for Exa API Scripts

## Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run individual test files
pytest tests/test_excel_export.py
pytest tests/test_integration.py

# Run a specific test
pytest tests/test_integration.py::test_websets_format_and_save_results
```

### Linting
```bash
flake8 src/
```

## Code Style Guidelines

- **Line Length**: Maximum 120 characters (set in .flake8)
- **Typing**: Use type hints for all functions (e.g., `def function(param: str) -> bool:`)
- **Docstrings**: Use triple-quoted docstrings for all functions and modules
- **Error Handling**: Use try/except blocks with specific exceptions 
- **Imports**: Group standard library imports first, then third-party, then local
- **Naming**: Use snake_case for functions and variables, PascalCase for classes
- **Logging**: Use print statements for console output
- **JSON Handling**: Use appropriate encoding and error handling for JSON
