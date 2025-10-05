"""
Invoice Parser Widget - Main Entry Point

This widget extracts structured data from invoice PDFs using AI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from utils.pdf_processor import extract_text_from_pdf, get_pdf_metadata
from utils.ai_parser import parse_invoice_with_ai
from utils.formatter import format_to_csv, format_to_json, create_summary_text
from utils.config import Config
from utils.logger import setup_logger


def setup_output_directory() -> Path:
    """
    Create and return the output directory.

    Returns:
        Path to output directory
    """
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    return output_dir


def find_invoice_file(file_path: str) -> str:
    """
    Find the invoice file, handling various path scenarios.

    Args:
        file_path: The file path from environment variable

    Returns:
        Valid file path

    Raises:
        FileNotFoundError: If file cannot be found
    """
    # Try the exact path first
    if Path(file_path).exists():
        return file_path

    # Try just the filename in current directory
    filename = Path(file_path).name
    if Path(filename).exists():
        return filename

    # Try looking for any PDF in current directory (for test runs)
    pdf_files = list(Path('.').glob('*.pdf'))
    if pdf_files:
        return str(pdf_files[0])

    # Try common upload directories
    common_paths = [
        Path('./uploads') / filename,
        Path('./') / filename,
        Path('../') / filename,
    ]

    for path in common_paths:
        if path.exists():
            return str(path)

    # If still not found, return original path (will fail with clear error)
    return file_path


def get_environment_inputs() -> dict:
    """
    Get and validate inputs from environment variables.

    Returns:
        Dictionary of validated inputs
    """
    # Get the invoice file path - Abyss provides file paths
    invoice_file = os.environ.get('invoice_file', 'invoice.pdf')

    # Try to find the actual file
    invoice_file = find_invoice_file(invoice_file)

    return {
        'invoice_file': invoice_file,
        'output_format': os.environ.get('output_format', 'csv'),
        'ai_provider': os.environ.get('ai_provider', 'openai'),
        'use_ocr': os.environ.get('use_ocr', 'false').lower() == 'true',
        'test_mode': os.environ.get('test_mode', 'false').lower() == 'true',
    }


def save_outputs(
    parsed_data: dict,
    output_format: str,
    output_dir: Path,
    logger
) -> None:
    """
    Save parsed data to output files.

    Args:
        parsed_data: Parsed invoice data
        output_format: Output format ('csv', 'json', or 'both')
        output_dir: Output directory path
        logger: Logger instance
    """
    output_files = []

    # Save based on format
    if output_format.lower() in ['csv', 'both']:
        logger.info("Generating CSV output...")
        csv_file = output_dir / 'invoice_data.csv'
        format_to_csv(parsed_data, csv_file)
        output_files.append('invoice_data.csv')

        # Check if line items CSV was created
        line_items_csv = output_dir / 'line_items.csv'
        if line_items_csv.exists():
            output_files.append('line_items.csv')

    if output_format.lower() in ['json', 'both']:
        logger.info("Generating JSON output...")
        json_file = output_dir / 'invoice_data.json'
        format_to_json(parsed_data, json_file)
        output_files.append('invoice_data.json')

    # Create summary text
    logger.info("Creating summary...")
    summary_file = output_dir / 'summary.txt'
    summary_text = create_summary_text(parsed_data)

    # Add output files list to summary
    summary_text += f"\n\nOUTPUT FILES:\n"
    for file in output_files:
        summary_text += f"  - {file}\n"

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)

    output_files.append('summary.txt')

    logger.info(f"Created {len(output_files)} output files")


def save_error_output(error: Exception, output_dir: Path) -> None:
    """
    Save error information to output file.

    Args:
        error: The exception that occurred
        output_dir: Output directory path
    """
    output_dir.mkdir(exist_ok=True)
    error_file = output_dir / 'error_log.txt'

    error_msg = [
        "=" * 50,
        "ERROR PROCESSING INVOICE",
        "=" * 50,
        "",
        f"Error: {str(error)}",
        "",
        "TROUBLESHOOTING:",
        "",
        "Common Issues:",
        "  1. PDF file not found or invalid path",
        "  2. PDF is password-protected or corrupted",
        "  3. PDF contains no readable text (try enabling OCR)",
        "  4. API key not set or invalid",
        "  5. Network issues connecting to AI service",
        "",
        "Solutions:",
        "  - Ensure the PDF file exists and is not password-protected",
        "  - Set the correct environment variable for your AI provider:",
        "    * OPENAI_API_KEY for OpenAI",
        "    * ANTHROPIC_API_KEY for Anthropic Claude",
        "  - Enable OCR for image-based PDFs (set use_ocr=true)",
        "  - Check your internet connection",
        "",
        "=" * 50,
    ]

    with open(error_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(error_msg))


def main():
    """Main entry point for the invoice parser widget."""

    # Setup
    output_dir = setup_output_directory()
    logger = setup_logger()

    logger.info("=" * 50)
    logger.info("INVOICE PARSER WIDGET")
    logger.info("=" * 50)

    try:
        # Get inputs
        logger.step(1, 4, "Reading configuration...")
        inputs = get_environment_inputs()

        invoice_file = inputs['invoice_file']
        output_format = Config.validate_output_format(inputs['output_format'])
        ai_provider = Config.validate_provider(inputs['ai_provider'])
        use_ocr = inputs['use_ocr']
        test_mode = inputs['test_mode']

        logger.info(f"Invoice file: {invoice_file}")
        logger.info(f"Output format: {output_format}")
        logger.info(f"AI provider: {ai_provider}")
        logger.info(f"OCR enabled: {use_ocr}")

        # Debug: Check if file exists
        if not Path(invoice_file).exists():
            logger.warning(f"File not found at: {invoice_file}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Files in current directory: {list(Path('.').glob('*.*'))[:10]}")
        else:
            logger.info(f"File found successfully: {Path(invoice_file).absolute()}")

        # Extract PDF metadata
        try:
            metadata = get_pdf_metadata(invoice_file)
            logger.info(f"PDF info: {metadata.get('num_pages', 0)} pages, "
                       f"{metadata.get('file_size_mb', 0)} MB")
        except Exception as e:
            logger.warning(f"Could not read PDF metadata: {e}")

        # Step 1: Extract text from PDF
        logger.step(2, 4, "Extracting text from PDF...")
        invoice_text = extract_text_from_pdf(invoice_file, use_ocr=use_ocr)

        logger.info(f"Extracted {len(invoice_text)} characters")

        if not invoice_text.strip():
            raise ValueError(
                "No text found in PDF. The invoice may be image-based or corrupted. "
                "Try enabling OCR."
            )

        # Step 2: Parse with AI
        logger.step(3, 4, f"Parsing invoice with {ai_provider.upper()}...")

        # Check if API key is available, otherwise use test mode
        if test_mode:
            logger.info("Test mode enabled - using mock parser")
            from utils.ai_parser import parse_invoice_mock
            parsed_data = parse_invoice_mock(invoice_text)
        else:
            # Check if API key exists
            api_key_available = False
            if ai_provider == 'openai' and os.environ.get('OPENAI_API_KEY'):
                api_key_available = True
            elif ai_provider == 'anthropic' and os.environ.get('ANTHROPIC_API_KEY'):
                api_key_available = True

            if not api_key_available:
                logger.warning(f"No {ai_provider.upper()} API key found - falling back to test mode")
                logger.info("Using mock parser for basic extraction")
                from utils.ai_parser import parse_invoice_mock
                parsed_data = parse_invoice_mock(invoice_text)
            else:
                parsed_data = parse_invoice_with_ai(invoice_text, ai_provider)

        logger.info("Invoice parsed successfully")
        logger.info(f"Found {len(parsed_data.get('line_items', []))} line items")

        # Step 3: Save outputs
        logger.step(4, 4, "Saving outputs...")
        save_outputs(parsed_data, output_format, output_dir, logger)

        # Success
        logger.info("=" * 50)
        logger.info("✅ PROCESSING COMPLETE!")
        logger.info("=" * 50)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        save_error_output(e, output_dir)
        return 1

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        save_error_output(e, output_dir)
        return 1

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        save_error_output(e, output_dir)
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        save_error_output(e, output_dir)
        raise

    finally:
        logger.info("Execution finished")


if __name__ == "__main__":
    sys.exit(main())