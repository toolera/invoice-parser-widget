"""PDF processing utilities with OCR support."""

import os
from pathlib import Path
from typing import Optional

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")


def validate_pdf_file(pdf_path: str) -> Path:
    """
    Validate PDF file exists and is readable.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a PDF or is too large
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    if pdf_path.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path}")

    # Check file size (max 5MB as per Abyss requirements)
    file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 5:
        raise ValueError(f"PDF file too large: {file_size_mb:.2f}MB (max 5MB)")

    return pdf_path


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> str:
    """
    Extract text from PDF file with optional OCR support.
    Handles multi-page invoices.

    Args:
        pdf_path: Path to the PDF file
        use_ocr: Whether to use OCR for image-based PDFs

    Returns:
        Extracted text content

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is invalid or extraction fails
    """
    # Validate PDF file
    pdf_path = validate_pdf_file(pdf_path)

    text = ""

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                raise ValueError("PDF is password-protected. Please provide an unencrypted version.")

            num_pages = len(pdf_reader.pages)

            if num_pages == 0:
                raise ValueError("PDF has no pages")

            # Extract text from all pages
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        # Clean up extracted text
        text = text.strip()

        # Check if we got any text
        if not text or len(text) < 10:
            error_msg = "No readable text found in PDF."
            if use_ocr:
                text = extract_text_with_ocr(pdf_path)
                if not text or len(text) < 10:
                    raise ValueError(
                        f"{error_msg} The invoice may be image-based. "
                        "OCR was attempted but no text was extracted."
                    )
            else:
                raise ValueError(
                    f"{error_msg} The invoice may be image-based or corrupted. "
                    "Try enabling OCR or provide a text-based PDF."
                )

        return text

    except PyPDF2.errors.PdfReadError as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"Unexpected error extracting text from PDF: {str(e)}")


def extract_text_with_ocr(pdf_path: Path) -> str:
    """
    Extract text from image-based PDF using OCR.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Extracted text via OCR

    Raises:
        ImportError: If required OCR libraries are not installed
        ValueError: If OCR extraction fails
    """
    try:
        import pdf2image
        import pytesseract
    except ImportError:
        raise ImportError(
            "OCR support requires pdf2image and pytesseract. "
            "Install with: pip install pdf2image pytesseract"
        )

    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)

        # Extract text from each image
        text_parts = []
        for image in images:
            page_text = pytesseract.image_to_string(image)
            if page_text.strip():
                text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    except Exception as e:
        raise ValueError(f"OCR extraction failed: {str(e)}")


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary containing PDF metadata
    """
    pdf_path = validate_pdf_file(pdf_path)

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            metadata = {
                'num_pages': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
                'file_size_mb': round(pdf_path.stat().st_size / (1024 * 1024), 2),
            }

            # Add PDF info if available
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                metadata.update({
                    'author': info.get('/Author', 'Unknown'),
                    'creator': info.get('/Creator', 'Unknown'),
                    'producer': info.get('/Producer', 'Unknown'),
                    'subject': info.get('/Subject', ''),
                    'title': info.get('/Title', ''),
                })

            return metadata

    except Exception as e:
        return {'error': str(e)}