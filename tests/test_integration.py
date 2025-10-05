"""Integration tests for the invoice parser."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def sample_pdf(temp_dir):
    """Create a sample PDF file for testing."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    pdf_path = temp_dir / 'test_invoice.pdf'

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "INVOICE")
    c.drawString(100, 730, "Invoice #: INV-2025-001")
    c.drawString(100, 710, "Date: 2025-01-15")
    c.drawString(100, 690, "")
    c.drawString(100, 670, "From: Test Company Inc.")
    c.drawString(100, 650, "123 Main St")
    c.drawString(100, 630, "Email: contact@testcompany.com")
    c.drawString(100, 610, "")
    c.drawString(100, 590, "To: Client Corp")
    c.drawString(100, 570, "456 Oak Ave")
    c.drawString(100, 550, "")
    c.drawString(100, 530, "Description: Web Development Services")
    c.drawString(100, 510, "Quantity: 10")
    c.drawString(100, 490, "Unit Price: $100.00")
    c.drawString(100, 470, "")
    c.drawString(100, 450, "Subtotal: $1,000.00")
    c.drawString(100, 430, "Tax (8%): $80.00")
    c.drawString(100, 410, "Total: $1,080.00")
    c.drawString(100, 390, "")
    c.drawString(100, 370, "Payment Terms: Net 30")
    c.save()

    return pdf_path


def test_full_workflow_with_mock(temp_dir, sample_pdf, monkeypatch):
    """Test full workflow using mock parser."""
    # Change to temp directory
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    try:
        # Set environment variables
        monkeypatch.setenv('invoice_file', str(sample_pdf))
        monkeypatch.setenv('output_format', 'both')
        monkeypatch.setenv('ai_provider', 'openai')
        monkeypatch.setenv('test_mode', 'true')

        # Import and run main
        from run import main

        # Create output directory
        (temp_dir / 'output').mkdir(exist_ok=True)

        # Run the widget
        result = main()

        # Check return code
        assert result == 0

        # Check outputs exist
        output_dir = temp_dir / 'output'
        assert (output_dir / 'summary.txt').exists()
        assert (output_dir / 'invoice_data.csv').exists()
        assert (output_dir / 'invoice_data.json').exists()

        # Check summary content
        summary = (output_dir / 'summary.txt').read_text()
        assert 'INVOICE PROCESSING COMPLETE' in summary

    finally:
        os.chdir(original_dir)


def test_error_handling_missing_file(temp_dir, monkeypatch):
    """Test error handling when PDF file is missing."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    try:
        monkeypatch.setenv('invoice_file', 'nonexistent.pdf')

        from run import main

        (temp_dir / 'output').mkdir(exist_ok=True)

        result = main()

        # Should return error code
        assert result == 1

        # Error log should exist
        assert (temp_dir / 'output' / 'error_log.txt').exists()

        error_log = (temp_dir / 'output' / 'error_log.txt').read_text()
        assert 'ERROR PROCESSING INVOICE' in error_log

    finally:
        os.chdir(original_dir)


def test_csv_output_format(temp_dir, sample_pdf, monkeypatch):
    """Test CSV only output."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    try:
        monkeypatch.setenv('invoice_file', str(sample_pdf))
        monkeypatch.setenv('output_format', 'csv')
        monkeypatch.setenv('test_mode', 'true')

        from run import main

        (temp_dir / 'output').mkdir(exist_ok=True)
        result = main()

        assert result == 0

        output_dir = temp_dir / 'output'
        assert (output_dir / 'invoice_data.csv').exists()
        assert not (output_dir / 'invoice_data.json').exists()

    finally:
        os.chdir(original_dir)


def test_json_output_format(temp_dir, sample_pdf, monkeypatch):
    """Test JSON only output."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)

    try:
        monkeypatch.setenv('invoice_file', str(sample_pdf))
        monkeypatch.setenv('output_format', 'json')
        monkeypatch.setenv('test_mode', 'true')

        from run import main

        (temp_dir / 'output').mkdir(exist_ok=True)
        result = main()

        assert result == 0

        output_dir = temp_dir / 'output'
        assert (output_dir / 'invoice_data.json').exists()
        assert not (output_dir / 'invoice_data.csv').exists()

    finally:
        os.chdir(original_dir)
