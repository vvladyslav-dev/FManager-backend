# Tests

This directory contains integration tests for the Form Manager API.

## Setup

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run specific test file:

```bash
pytest tests/test_form_submission.py
```

Run with verbose output:

```bash
pytest -v
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py` - Test fixtures and configuration
- `test_form_submission.py` - Tests for form submission flow
- `test_form_management.py` - Tests for form CRUD operations

## Test Database

Tests use an in-memory SQLite database, so no external database setup is required.

## Azure Storage Mocking

Azure Storage is automatically mocked in tests, so no Azure credentials are needed for testing.

