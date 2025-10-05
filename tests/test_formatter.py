"""Tests for formatter module."""

import pytest
from pathlib import Path
import tempfile
import shutil
from utils.formatter import format_to_csv, format_to_json, create_summary_text


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    return {
        'vendor_name': 'Test Company Inc.',
        'vendor_address': '123 Main St, City, State 12345',
        'vendor_email': 'contact@testcompany.com',
        'vendor_phone': '+1-555-123-4567',
        'invoice_number': 'INV-2025-001',
        'invoice_date': '2025-01-15',
        'due_date': '2025-02-15',
        'customer_name': 'Client Corp',
        'customer_address': '456 Oak Ave, Town, State 67890',
        'subtotal': 1000.00,
        'tax_amount': 80.00,
        'tax_rate': 8.0,
        'total_amount': 1080.00,
        'currency': 'USD',
        'payment_terms': 'Net 30',
        'line_items': [
            {
                'description': 'Web Development Services',
                'quantity': 10,
                'unit_price': 100.00,
                'total': 1000.00
            }
        ]
    }


def test_format_to_csv(temp_dir, sample_invoice_data):
    """Test CSV formatting."""
    output_file = temp_dir / 'test_invoice.csv'

    format_to_csv(sample_invoice_data, output_file)

    assert output_file.exists()
    content = output_file.read_text()
    assert 'Field,Value' in content
    assert 'Vendor Name,Test Company Inc.' in content
    assert 'Total Amount,1080.0' in content


def test_format_to_csv_with_line_items(temp_dir, sample_invoice_data):
    """Test CSV formatting creates line items file."""
    output_file = temp_dir / 'test_invoice.csv'

    format_to_csv(sample_invoice_data, output_file)

    line_items_file = temp_dir / 'line_items.csv'
    assert line_items_file.exists()

    content = line_items_file.read_text()
    assert 'description' in content
    assert 'Web Development Services' in content


def test_format_to_csv_empty_line_items(temp_dir):
    """Test CSV formatting with empty line items."""
    data = {'vendor_name': 'Test', 'line_items': []}
    output_file = temp_dir / 'test.csv'

    format_to_csv(data, output_file)

    assert output_file.exists()
    line_items_file = temp_dir / 'line_items.csv'
    assert not line_items_file.exists()


def test_format_to_csv_none_values(temp_dir):
    """Test CSV formatting with None values."""
    data = {'vendor_name': None, 'total_amount': None}
    output_file = temp_dir / 'test.csv'

    format_to_csv(data, output_file)

    assert output_file.exists()
    content = output_file.read_text()
    assert 'Vendor Name,' in content  # None should become empty string


def test_format_to_csv_empty_data(temp_dir):
    """Test CSV formatting with empty data raises error."""
    output_file = temp_dir / 'test.csv'

    with pytest.raises(ValueError, match="Cannot format empty data"):
        format_to_csv({}, output_file)


def test_format_to_json(temp_dir, sample_invoice_data):
    """Test JSON formatting."""
    output_file = temp_dir / 'test_invoice.json'

    format_to_json(sample_invoice_data, output_file)

    assert output_file.exists()
    import json
    data = json.loads(output_file.read_text())
    assert data['vendor_name'] == 'Test Company Inc.'
    assert data['total_amount'] == 1080.00


def test_format_to_json_empty_data(temp_dir):
    """Test JSON formatting with empty data raises error."""
    output_file = temp_dir / 'test.json'

    with pytest.raises(ValueError, match="Cannot format empty data"):
        format_to_json({}, output_file)


def test_create_summary_text(sample_invoice_data):
    """Test summary text creation."""
    summary = create_summary_text(sample_invoice_data)

    assert 'INVOICE PROCESSING COMPLETE' in summary
    assert 'Test Company Inc.' in summary
    assert 'INV-2025-001' in summary
    assert '1080.0' in summary
    assert 'Web Development Services' in summary


def test_create_summary_text_no_line_items():
    """Test summary with no line items."""
    data = {'vendor_name': 'Test', 'line_items': []}
    summary = create_summary_text(data)

    assert 'No line items found' in summary


def test_csv_with_mixed_line_item_fields(temp_dir):
    """Test CSV with line items having different fields."""
    data = {
        'vendor_name': 'Test',
        'line_items': [
            {'description': 'Item 1', 'quantity': 1},
            {'description': 'Item 2', 'unit_price': 10.00},
        ]
    }
    output_file = temp_dir / 'test.csv'

    format_to_csv(data, output_file)

    line_items_file = temp_dir / 'line_items.csv'
    assert line_items_file.exists()

    content = line_items_file.read_text()
    # Should have all fields
    assert 'description' in content
    assert 'quantity' in content
    assert 'unit_price' in content
