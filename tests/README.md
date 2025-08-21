# Tests Directory

This directory contains all test files and test-related utilities for the Galveston Reservation System.

## Test Files

- `test_calendar.py` - Google Calendar API integration tests
- `test_calendar_sync.py` - Calendar synchronization tests  
- `test_email.py` - Email service functionality tests
- `test_setup.py` - System setup and configuration tests
- `test_simple_calendar.py` - Basic calendar functionality tests
- `test_simple_scraper.py` - Web scraping tests
- `test_improved_scraper.py` - Enhanced scraping tests

## Test Utilities

- `simple_server.py` - Lightweight Flask server for testing
- `test_calendar.html` - Calendar display test page
- `sample_page.html` - Sample HTML for scraping tests

## Test Data

- `calendar_comparison_results.json` - Sample calendar comparison output

## Running Tests

```bash
# From project root
python -m pytest tests/

# Run specific test
python tests/test_calendar.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Environment

Make sure to set up test environment variables in `.env` or use a separate `.env.test` file for testing credentials.
