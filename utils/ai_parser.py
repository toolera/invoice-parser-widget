"""AI-powered invoice parsing utilities."""

import os
import json
import re
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


def validate_api_key(provider: str) -> str:
    """
    Validate API key exists for the specified provider.

    Args:
        provider: AI provider name ('openai' or 'anthropic')

    Returns:
        API key string

    Raises:
        ValueError: If API key is not found
    """
    provider = provider.lower()

    if provider == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please provide your OpenAI API key."
            )
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")
        return api_key

    elif provider == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please provide your Anthropic API key."
            )
        if Anthropic is None:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        return api_key

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def build_extraction_prompt(invoice_text: str) -> str:
    """
    Build the AI prompt for invoice data extraction.

    Args:
        invoice_text: Raw text from invoice

    Returns:
        Formatted prompt string
    """
    return f"""You are an expert invoice data extraction system. Extract the following information from this invoice:

REQUIRED FIELDS:
- vendor_name: Company name of the seller
- vendor_address: Full address of vendor
- vendor_email: Vendor contact email
- vendor_phone: Vendor contact phone
- invoice_number: Invoice/reference number
- invoice_date: Date of invoice (YYYY-MM-DD format)
- due_date: Payment due date (YYYY-MM-DD format)
- customer_name: Buyer/customer name
- customer_address: Customer full address
- subtotal: Subtotal before tax (numeric value only)
- tax_amount: Tax amount (numeric value only)
- tax_rate: Tax percentage (numeric value only)
- total_amount: Final total (numeric value only)
- currency: Currency code (USD, EUR, GBP, etc.)
- payment_terms: Payment terms/conditions
- line_items: Array of items, each with:
  - description: Item/service description
  - quantity: Quantity (numeric)
  - unit_price: Price per unit (numeric)
  - total: Line item total (numeric)

IMPORTANT RULES:
1. Return ONLY valid JSON - no markdown, no explanations
2. If a field is not found in the invoice, use null
3. For numeric fields, extract only the number (no currency symbols)
4. Dates must be in YYYY-MM-DD format
5. Ensure line_items is always an array (can be empty [])
6. Double-check your JSON is valid before responding

INVOICE TEXT:
{invoice_text}

JSON OUTPUT:"""


def clean_json_response(response_text: str) -> str:
    """
    Clean AI response to extract valid JSON.

    Args:
        response_text: Raw AI response

    Returns:
        Cleaned JSON string

    Raises:
        ValueError: If no valid JSON found
    """
    response_text = response_text.strip()

    # Remove markdown code blocks
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    elif response_text.startswith('```'):
        response_text = response_text[3:]

    if response_text.endswith('```'):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Try to find JSON object in the response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)

    return response_text


def validate_parsed_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean parsed invoice data.

    Args:
        data: Parsed invoice dictionary

    Returns:
        Validated and cleaned data dictionary

    Raises:
        ValueError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Parsed data must be a dictionary")

    # Ensure line_items is a list
    if 'line_items' in data:
        if data['line_items'] is None:
            data['line_items'] = []
        elif not isinstance(data['line_items'], list):
            data['line_items'] = []

    # Convert numeric strings to proper format
    numeric_fields = ['subtotal', 'tax_amount', 'tax_rate', 'total_amount']
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                # Remove any non-numeric characters except decimal point
                value_str = str(data[field]).replace(',', '')
                data[field] = float(value_str)
            except (ValueError, TypeError):
                data[field] = None

    return data


def parse_invoice_with_ai(
    invoice_text: str,
    provider: str = 'openai',
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use AI to intelligently parse invoice data.
    Supports OpenAI GPT-4 and Anthropic Claude.

    Args:
        invoice_text: Extracted text from invoice
        provider: AI provider ('openai' or 'anthropic')
        model: Specific model to use (optional)

    Returns:
        Parsed invoice data as dictionary

    Raises:
        ValueError: If parsing fails or API key is missing
        ImportError: If required library is not installed
    """
    if not invoice_text or len(invoice_text.strip()) < 10:
        raise ValueError("Invoice text is empty or too short to parse")

    provider = provider.lower()

    # Validate API key
    api_key = validate_api_key(provider)

    # Build prompt
    prompt = build_extraction_prompt(invoice_text)

    # Call AI provider
    try:
        if provider == 'anthropic':
            client = Anthropic(api_key=api_key)
            model = model or "claude-3-5-sonnet-20241022"

            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text

        else:  # OpenAI
            client = OpenAI(api_key=api_key)
            model = model or "gpt-4"

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content

    except Exception as e:
        raise ValueError(f"AI API call failed: {str(e)}")

    # Clean and parse JSON
    try:
        result = clean_json_response(result)
        parsed_data = json.loads(result)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {result[:200]}")

    # Validate and clean data
    parsed_data = validate_parsed_data(parsed_data)

    return parsed_data


def parse_invoice_mock(invoice_text: str) -> Dict[str, Any]:
    """
    Mock parser for testing without API calls.
    Extracts basic information using regex patterns.

    Args:
        invoice_text: Invoice text

    Returns:
        Basic parsed data dictionary
    """
    mock_data = {
        'vendor_name': None,
        'vendor_address': None,
        'vendor_email': None,
        'vendor_phone': None,
        'invoice_number': None,
        'invoice_date': None,
        'due_date': None,
        'customer_name': None,
        'customer_address': None,
        'subtotal': None,
        'tax_amount': None,
        'tax_rate': None,
        'total_amount': None,
        'currency': 'USD',
        'payment_terms': None,
        'line_items': []
    }

    # Simple pattern matching
    # Invoice number
    inv_match = re.search(r'(?:invoice|inv)[#\s:]*([A-Z0-9-]+)', invoice_text, re.IGNORECASE)
    if inv_match:
        mock_data['invoice_number'] = inv_match.group(1)

    # Total amount
    total_match = re.search(r'(?:total|amount due)[:\s]*\$?\s*([\d,]+\.?\d*)', invoice_text, re.IGNORECASE)
    if total_match:
        mock_data['total_amount'] = float(total_match.group(1).replace(',', ''))

    # Email
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', invoice_text)
    if email_match:
        mock_data['vendor_email'] = email_match.group(1)

    return mock_data