"""Tests for AI parser module."""

import pytest
import os
from utils.ai_parser import (
    validate_api_key,
    build_extraction_prompt,
    clean_json_response,
    validate_parsed_data,
    parse_invoice_mock
)


def test_validate_api_key_openai_missing():
    """Test validation fails when OpenAI key is missing."""
    # Ensure key is not set
    old_key = os.environ.pop('OPENAI_API_KEY', None)

    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
        validate_api_key('openai')

    # Restore if it was set
    if old_key:
        os.environ['OPENAI_API_KEY'] = old_key


def test_validate_api_key_anthropic_missing():
    """Test validation fails when Anthropic key is missing."""
    old_key = os.environ.pop('ANTHROPIC_API_KEY', None)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
        validate_api_key('anthropic')

    if old_key:
        os.environ['ANTHROPIC_API_KEY'] = old_key


def test_validate_api_key_invalid_provider():
    """Test validation fails for invalid provider."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        validate_api_key('invalid')


def test_build_extraction_prompt():
    """Test prompt building."""
    invoice_text = "Test invoice content"
    prompt = build_extraction_prompt(invoice_text)

    assert "expert invoice data extraction" in prompt
    assert invoice_text in prompt
    assert "vendor_name" in prompt
    assert "line_items" in prompt


def test_clean_json_response_simple():
    """Test cleaning simple JSON response."""
    response = '{"vendor_name": "Test"}'
    cleaned = clean_json_response(response)
    assert cleaned == '{"vendor_name": "Test"}'


def test_clean_json_response_with_markdown():
    """Test cleaning JSON with markdown code blocks."""
    response = '```json\n{"vendor_name": "Test"}\n```'
    cleaned = clean_json_response(response)
    assert '```' not in cleaned
    assert '{"vendor_name": "Test"}' in cleaned


def test_clean_json_response_with_generic_markdown():
    """Test cleaning JSON with generic code blocks."""
    response = '```\n{"vendor_name": "Test"}\n```'
    cleaned = clean_json_response(response)
    assert '```' not in cleaned


def test_clean_json_response_with_text():
    """Test cleaning JSON embedded in text."""
    response = 'Here is the data: {"vendor_name": "Test"} end'
    cleaned = clean_json_response(response)
    assert '{"vendor_name": "Test"}' in cleaned


def test_validate_parsed_data_valid():
    """Test validation of valid data."""
    data = {
        'vendor_name': 'Test',
        'total_amount': '1000.00',
        'line_items': [{'description': 'Item 1'}]
    }

    validated = validate_parsed_data(data)

    assert validated['vendor_name'] == 'Test'
    assert validated['total_amount'] == 1000.00
    assert isinstance(validated['line_items'], list)


def test_validate_parsed_data_null_line_items():
    """Test validation converts null line_items to list."""
    data = {'vendor_name': 'Test', 'line_items': None}

    validated = validate_parsed_data(data)

    assert validated['line_items'] == []


def test_validate_parsed_data_invalid_line_items():
    """Test validation converts invalid line_items to list."""
    data = {'vendor_name': 'Test', 'line_items': 'invalid'}

    validated = validate_parsed_data(data)

    assert validated['line_items'] == []


def test_validate_parsed_data_numeric_conversion():
    """Test numeric field conversion."""
    data = {
        'subtotal': '1,000.50',
        'tax_amount': '80',
        'total_amount': 1080.50
    }

    validated = validate_parsed_data(data)

    assert validated['subtotal'] == 1000.50
    assert validated['tax_amount'] == 80.0
    assert validated['total_amount'] == 1080.50


def test_validate_parsed_data_invalid_numeric():
    """Test invalid numeric values become None."""
    data = {'total_amount': 'invalid'}

    validated = validate_parsed_data(data)

    assert validated['total_amount'] is None


def test_validate_parsed_data_not_dict():
    """Test validation fails for non-dict."""
    with pytest.raises(ValueError, match="must be a dictionary"):
        validate_parsed_data("not a dict")


def test_parse_invoice_mock():
    """Test mock parser."""
    invoice_text = """
    Invoice #INV-2025-001
    Total: $1,250.00
    Email: vendor@example.com
    """

    result = parse_invoice_mock(invoice_text)

    assert isinstance(result, dict)
    assert result['invoice_number'] == 'INV-2025-001'
    assert result['total_amount'] == 1250.00
    assert result['vendor_email'] == 'vendor@example.com'
    assert isinstance(result['line_items'], list)


def test_parse_invoice_mock_minimal():
    """Test mock parser with minimal data."""
    invoice_text = "Random text with no invoice data"

    result = parse_invoice_mock(invoice_text)

    assert isinstance(result, dict)
    assert 'vendor_name' in result
    assert 'line_items' in result
    assert result['currency'] == 'USD'
