# 🧾 Invoice Parser Widget

AI-powered invoice data extraction widget that converts PDF invoices into structured CSV/JSON data.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Improvements Summary](#improvements-summary)
- [API Reference](#api-reference)

---

## 🎯 Overview

This widget extracts structured data from invoice PDFs using AI (OpenAI GPT-4 or Anthropic Claude). It handles text-based and image-based PDFs, validates inputs, and outputs clean CSV/JSON files with comprehensive error handling and logging.

**Key Capabilities:**
- Extract vendor, customer, invoice details, line items, and financial data
- Support for OpenAI GPT-4 and Anthropic Claude
- OCR support for image-based PDFs
- Multiple output formats (CSV, JSON, or both)
- Comprehensive error handling and validation
- Test mode with mock parser

---

## ✨ Features

### Core Features
- ✅ **AI-Powered Parsing** - Uses GPT-4 or Claude for intelligent data extraction
- ✅ **Multi-Format Output** - CSV, JSON, or both formats
- ✅ **OCR Support** - Extract text from image-based PDFs
- ✅ **Robust Validation** - Validates files, API keys, and extracted data
- ✅ **Error Handling** - Comprehensive error messages and troubleshooting guides
- ✅ **Logging System** - Step-by-step progress tracking
- ✅ **Test Mode** - Mock parser for testing without API calls

### Extracted Data Fields
- Vendor information (name, address, email, phone)
- Customer information (name, address)
- Invoice details (number, date, due date)
- Financial data (subtotal, tax, total, currency)
- Line items (description, quantity, unit price, total)
- Payment terms

---

## 📁 Project Structure

```
invoice-parser-widget/
│
├── run.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── requirements.system         # System dependencies (apt packages)
├── pytest.ini                  # Test configuration
├── .gitignore                  # Git ignore rules
├── .env                        # Environment variables (not in git)
│
├── utils/                      # Core utility modules
│   ├── __init__.py            # Module exports
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging system
│   ├── pdf_processor.py       # PDF extraction & OCR
│   ├── ai_parser.py           # AI parsing & validation
│   └── formatter.py           # Output formatting (CSV/JSON)
│
├── tests/                      # Test suite (46 tests, 74% coverage)
│   ├── __init__.py
│   ├── test_config.py         # Configuration tests (16 tests)
│   ├── test_formatter.py      # Formatter tests (10 tests)
│   ├── test_ai_parser.py      # AI parser tests (16 tests)
│   └── test_integration.py    # Integration tests (4 tests)
│
└── output/                     # Generated output files
    └── .gitkeep               # Keep directory in git
```

### Module Descriptions

#### `run.py`
Main entry point that orchestrates the entire workflow:
- Reads environment variables
- Validates configuration
- Extracts text from PDF
- Parses invoice with AI
- Saves output files
- Handles errors gracefully

#### `utils/config.py`
Configuration management and validation:
- Provider validation (OpenAI, Anthropic)
- Output format validation (CSV, JSON, both)
- API key retrieval
- Model configuration

#### `utils/logger.py`
Logging system with:
- Console and file output
- Timestamped messages
- Step-by-step progress tracking
- Multiple log levels

#### `utils/pdf_processor.py`
PDF processing with:
- File validation (size, type, existence)
- Text extraction from PDFs
- OCR support for image-based PDFs
- Metadata extraction
- Password protection detection

#### `utils/ai_parser.py`
AI-powered parsing with:
- API key validation
- Structured prompt generation
- JSON response cleaning
- Data validation and type conversion
- Mock parser for testing

#### `utils/formatter.py`
Output formatting with:
- CSV generation (main data + line items)
- JSON generation
- Summary text creation
- Edge case handling (empty/null values)

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd invoice-parser-widget
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install System Dependencies (Optional - for OCR)
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr

# macOS
brew install poppler tesseract
```

### 4. Set Environment Variables
Create a `.env` file:
```bash
# Required: Choose one AI provider
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Configure behavior
invoice_file=invoice.pdf
output_format=csv
ai_provider=openai
use_ocr=false
test_mode=false
```

---

## 💻 Usage

### Basic Usage
```bash
python run.py
```

### With Environment Variables
```bash
export invoice_file=my_invoice.pdf
export output_format=json
export ai_provider=anthropic
python run.py
```

### Using Test Mode (No API Calls)
```bash
export test_mode=true
python run.py
```

### Enable OCR for Image-Based PDFs
```bash
export use_ocr=true
python run.py
```

### Expected Output
After successful execution, the `output/` directory will contain:
- `invoice_data.csv` - Main invoice data
- `line_items.csv` - Line items (if present)
- `invoice_data.json` - JSON format (if selected)
- `summary.txt` - Human-readable summary

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `invoice_file` | `invoice.pdf` | Any PDF path | Path to invoice PDF |
| `output_format` | `csv` | `csv`, `json`, `both` | Output format |
| `ai_provider` | `openai` | `openai`, `anthropic` | AI provider |
| `use_ocr` | `false` | `true`, `false` | Enable OCR processing |
| `test_mode` | `false` | `true`, `false` | Use mock parser |
| `OPENAI_API_KEY` | - | API key | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | API key | Anthropic API key |

### Supported File Formats
- **Input:** PDF files (up to 5MB)
- **Output:** CSV, JSON, TXT

### AI Models
- **OpenAI:** GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic:** Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet

---

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run with Coverage
```bash
python -m pytest tests/ -v --cov=utils --cov-report=term-missing
```

### Run Specific Test Modules
```bash
python -m pytest tests/test_config.py -v
python -m pytest tests/test_formatter.py -v
python -m pytest tests/test_ai_parser.py -v
python -m pytest tests/test_integration.py -v
```

### Test Results
- **Total Tests:** 46
- **Passed:** 46 ✅
- **Failed:** 0
- **Code Coverage:** 74%

#### Coverage by Module
| Module | Coverage | Lines |
|--------|----------|-------|
| utils/__init__.py | 100% | 4 |
| utils/formatter.py | 100% | 52 |
| utils/config.py | 95% | 39 |
| utils/logger.py | 76% | 37 |
| utils/ai_parser.py | 65% | 98 |
| utils/pdf_processor.py | 54% | 78 |

---

## 📈 Improvements Summary

### What Was Improved

#### 1. **New Modules Added**
- `utils/config.py` - Configuration management
- `utils/logger.py` - Logging system
- `utils/__init__.py` - Module structure

#### 2. **Enhanced Modules**
- `run.py` - Better error handling, logging, validation
- `utils/pdf_processor.py` - OCR support, validation, metadata
- `utils/ai_parser.py` - Better validation, mock parser
- `utils/formatter.py` - Edge case handling, enhanced summaries

#### 3. **Testing Infrastructure**
- 46 comprehensive tests (unit + integration)
- 74% code coverage
- Test fixtures and utilities
- Mock parser for API-free testing

#### 4. **Code Quality**
- Type hints throughout
- Comprehensive docstrings
- Better error messages
- Input validation at all levels
- Security improvements

### Key Improvements

✅ **Configuration Management** - Centralized validation and configuration
✅ **Logging System** - Step-by-step progress tracking
✅ **OCR Support** - Handle image-based PDFs
✅ **Error Handling** - Comprehensive validation and user-friendly errors
✅ **Test Coverage** - 46 tests with 74% coverage
✅ **Mock Parser** - Test without API calls
✅ **Enhanced Output** - Better formatting and summaries
✅ **Type Safety** - Type hints throughout codebase
✅ **Documentation** - Complete API reference and guides
✅ **Security** - File validation, size limits, sanitization

---

## 📚 API Reference

### Main Functions

#### `main()`
Main entry point that orchestrates the workflow.

**Returns:** `int` - Exit code (0 = success, 1 = error)

#### `extract_text_from_pdf(pdf_path, use_ocr=False)`
Extract text from PDF file.

**Parameters:**
- `pdf_path` (str): Path to PDF file
- `use_ocr` (bool): Enable OCR for image-based PDFs

**Returns:** `str` - Extracted text

**Raises:**
- `FileNotFoundError`: If PDF doesn't exist
- `ValueError`: If PDF is invalid or unreadable

#### `parse_invoice_with_ai(invoice_text, provider='openai', model=None)`
Parse invoice text using AI.

**Parameters:**
- `invoice_text` (str): Extracted invoice text
- `provider` (str): AI provider ('openai' or 'anthropic')
- `model` (str): Specific model to use (optional)

**Returns:** `dict` - Parsed invoice data

**Raises:**
- `ValueError`: If API key is missing or parsing fails
- `ImportError`: If required library is not installed

#### `format_to_csv(parsed_data, output_path)`
Format parsed data to CSV files.

**Parameters:**
- `parsed_data` (dict): Parsed invoice data
- `output_path` (Path): Output file path

**Creates:**
- Main CSV with invoice data
- Separate CSV for line items (if present)

#### `format_to_json(parsed_data, output_path)`
Format parsed data to JSON file.

**Parameters:**
- `parsed_data` (dict): Parsed invoice data
- `output_path` (Path): Output file path

### Data Structure

#### Parsed Invoice Data
```python
{
    "vendor_name": str,
    "vendor_address": str,
    "vendor_email": str,
    "vendor_phone": str,
    "invoice_number": str,
    "invoice_date": str,  # YYYY-MM-DD
    "due_date": str,      # YYYY-MM-DD
    "customer_name": str,
    "customer_address": str,
    "subtotal": float,
    "tax_amount": float,
    "tax_rate": float,
    "total_amount": float,
    "currency": str,      # USD, EUR, etc.
    "payment_terms": str,
    "line_items": [
        {
            "description": str,
            "quantity": float,
            "unit_price": float,
            "total": float
        }
    ]
}
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. PDF Not Found
**Error:** `FileNotFoundError: PDF file not found`

**Solution:** Check the file path and ensure the PDF exists
```bash
export invoice_file=/full/path/to/invoice.pdf
```

#### 2. API Key Missing
**Error:** `ValueError: OPENAI_API_KEY environment variable not set`

**Solution:** Set the API key in your environment
```bash
export OPENAI_API_KEY=your_key_here
```

#### 3. No Text Extracted
**Error:** `ValueError: No readable text found in PDF`

**Solution:** Enable OCR for image-based PDFs
```bash
export use_ocr=true
```

#### 4. Password-Protected PDF
**Error:** `ValueError: PDF is password-protected`

**Solution:** Remove password protection or use an unencrypted version

#### 5. File Too Large
**Error:** `ValueError: PDF file too large: X.XX MB (max 5MB)`

**Solution:** Compress the PDF or split into smaller files

---

## 🔒 Security Considerations

- API keys are never logged or exposed
- File paths are validated before processing
- File size limits prevent memory issues
- Input sanitization prevents injection attacks
- OCR libraries may have vulnerabilities (keep updated)

---

## 🚦 Requirements

### Python Dependencies
- PyPDF2 >= 3.0.1
- openai >= 1.12.0
- anthropic >= 0.18.1
- pdf2image >= 1.16.3 (for OCR)
- pytesseract >= 0.3.10 (for OCR)
- pytest >= 7.4.3 (for testing)

### System Dependencies (Optional)
- poppler-utils (for OCR)
- tesseract-ocr (for OCR)

### System Requirements
- Python 3.10+
- 512 MB RAM or less
- 4 vCPUs or less (Abyss platform requirement)

---

## 📝 License

This project is designed for the Abyss AI Widget platform.

---

## 🤝 Contributing

This is a widget for the Abyss platform. For issues or improvements:
1. Run tests before submitting changes
2. Maintain backward compatibility
3. Add tests for new features
4. Update documentation

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review test cases for examples
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed

---

## 🎯 Future Enhancements

- [ ] Multi-language invoice support
- [ ] Batch processing (multiple invoices)
- [ ] Advanced OCR with layout analysis
- [ ] Duplicate invoice detection
- [ ] Excel output format
- [ ] Database integration
- [ ] Automatic amount validation
- [ ] Invoice categorization

---

**Built with ❤️ for the Abyss AI Widget Platform**
