"""Output formatting utilities for invoice data."""

import csv
import json
from pathlib import Path
from typing import Dict, Any, List


def format_to_csv(parsed_data: Dict[str, Any], output_path: Path) -> None:
    """
    Convert parsed invoice data to CSV format.
    Creates two files: main invoice data + line items.

    Args:
        parsed_data: Parsed invoice dictionary
        output_path: Path for the main CSV file

    Raises:
        ValueError: If parsed_data is invalid
    """
    if not parsed_data:
        raise ValueError("Cannot format empty data to CSV")

    output_path = Path(output_path)

    # Main invoice data
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Field', 'Value'])

        for key, value in parsed_data.items():
            if key != 'line_items':
                # Convert None to empty string for better CSV readability
                display_value = value if value is not None else ''
                writer.writerow([key.replace('_', ' ').title(), display_value])

    # Line items in separate file
    line_items = parsed_data.get('line_items', [])
    if line_items and isinstance(line_items, list) and len(line_items) > 0:
        items_path = output_path.parent / 'line_items.csv'

        # Extract all possible field names from all items
        all_fields = set()
        for item in line_items:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        if all_fields:
            fieldnames = sorted(list(all_fields))

            with open(items_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Write each item, filling missing fields with empty strings
                for item in line_items:
                    if isinstance(item, dict):
                        row = {field: item.get(field, '') for field in fieldnames}
                        writer.writerow(row)


def format_to_json(parsed_data: Dict[str, Any], output_path: Path) -> None:
    """
    Save parsed data as formatted JSON.

    Args:
        parsed_data: Parsed invoice dictionary
        output_path: Path for the JSON file

    Raises:
        ValueError: If parsed_data is invalid
    """
    if not parsed_data:
        raise ValueError("Cannot format empty data to JSON")

    output_path = Path(output_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)


def create_summary_text(parsed_data: Dict[str, Any]) -> str:
    """
    Create a human-readable summary of the parsed invoice.

    Args:
        parsed_data: Parsed invoice dictionary

    Returns:
        Formatted summary string
    """
    summary_lines = [
        "=" * 50,
        "INVOICE PROCESSING COMPLETE",
        "=" * 50,
        "",
        "VENDOR INFORMATION:",
        f"  Name: {parsed_data.get('vendor_name', 'N/A')}",
        f"  Address: {parsed_data.get('vendor_address', 'N/A')}",
        f"  Email: {parsed_data.get('vendor_email', 'N/A')}",
        f"  Phone: {parsed_data.get('vendor_phone', 'N/A')}",
        "",
        "INVOICE DETAILS:",
        f"  Invoice Number: {parsed_data.get('invoice_number', 'N/A')}",
        f"  Invoice Date: {parsed_data.get('invoice_date', 'N/A')}",
        f"  Due Date: {parsed_data.get('due_date', 'N/A')}",
        "",
        "CUSTOMER INFORMATION:",
        f"  Name: {parsed_data.get('customer_name', 'N/A')}",
        f"  Address: {parsed_data.get('customer_address', 'N/A')}",
        "",
        "FINANCIAL SUMMARY:",
        f"  Subtotal: {parsed_data.get('currency', 'USD')} {parsed_data.get('subtotal', '0.00')}",
        f"  Tax ({parsed_data.get('tax_rate', '0')}%): {parsed_data.get('currency', 'USD')} {parsed_data.get('tax_amount', '0.00')}",
        f"  Total: {parsed_data.get('currency', 'USD')} {parsed_data.get('total_amount', '0.00')}",
        "",
        "LINE ITEMS:",
    ]

    line_items = parsed_data.get('line_items', [])
    if line_items:
        summary_lines.append(f"  Total Items: {len(line_items)}")
        for i, item in enumerate(line_items, 1):
            if isinstance(item, dict):
                desc = item.get('description', 'N/A')
                qty = item.get('quantity', 'N/A')
                price = item.get('unit_price', 'N/A')
                total = item.get('total', 'N/A')
                summary_lines.append(f"  {i}. {desc} - Qty: {qty}, Price: {price}, Total: {total}")
    else:
        summary_lines.append("  No line items found")

    summary_lines.extend([
        "",
        "PAYMENT TERMS:",
        f"  {parsed_data.get('payment_terms', 'N/A')}",
        "",
        "=" * 50,
    ])

    return "\n".join(summary_lines)