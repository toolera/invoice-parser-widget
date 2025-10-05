# Abyss Platform Troubleshooting Guide

## ❌ Issue: "File not found" Error on Test Run

### Problem
```
ERROR - File not found: PDF file not found: product_run/253/68e2306d2038a/...pdf
```

### Root Cause
The Abyss platform provides a file path in the environment variable, but the actual uploaded file may be in a different location during test runs.

### ✅ Solutions Implemented

#### 1. Smart File Discovery
The widget now tries multiple strategies to find the uploaded file:

1. **Exact path** - Try the path provided by Abyss
2. **Filename only** - Look for the file in current directory
3. **Any PDF** - Find any PDF file in current directory (test mode)
4. **Common paths** - Check uploads/, ./, ../ directories

#### 2. Debug Logging
Added comprehensive logging to help troubleshoot:
- Current working directory
- Files in current directory
- File existence checks

### 🔧 How to Debug on Abyss Platform

When you see the error, check the logs for these lines:

```
INFO - Current working directory: /path/to/working/dir
INFO - Files in current directory: [list of files]
```

This will tell you:
1. Where the widget is running
2. What files are actually available

### 📋 Checklist for Test Run

Before running test on Abyss:

1. **Upload a Real PDF Invoice**
   - Use a real invoice PDF (not a dummy file)
   - File should be under 5MB
   - File should contain readable text

2. **Set Environment Variables**
   - For TEST RUN on Abyss, you might need to provide:
     - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - Optional variables:
     - `test_mode=true` (to use mock parser - no API key needed)
     - `use_ocr=true` (if invoice is image-based)

3. **Check File Field Configuration**
   - Field Name: `invoice_file`
   - Type: File
   - Accept: `.pdf` only
   - Required: Yes

### 🎯 Recommended Test Configuration

**For First Test (No API Key Required):**
```bash
# Environment Variables to set on Abyss:
test_mode=true
output_format=csv
ai_provider=openai
use_ocr=false
```

**Upload:** Any PDF invoice file

**Expected Output:**
- invoice_data.csv (basic fields)
- summary.txt (summary report)

**For Full Test (Requires API Key):**
```bash
# Environment Variables:
OPENAI_API_KEY=sk-...your-key...
output_format=both
ai_provider=openai
use_ocr=false
```

**Upload:** Real invoice PDF

**Expected Output:**
- invoice_data.csv (complete extraction)
- line_items.csv (if invoice has line items)
- invoice_data.json (JSON format)
- summary.txt (detailed summary)

### 🐛 Common Issues & Solutions

#### Issue 1: File Not Found
**Symptoms:** `FileNotFoundError: PDF file not found`

**Solution:**
- Widget now automatically searches for the file
- Check debug logs to see where it's looking
- Ensure file was actually uploaded

#### Issue 2: Permission Denied
**Symptoms:** `PermissionError` when reading file

**Solution:**
- File permissions issue on Abyss platform
- Contact Abyss support
- Widget cannot fix this

#### Issue 3: API Key Missing
**Symptoms:** `ValueError: OPENAI_API_KEY environment variable not set`

**Solution:**
- Set API key as environment variable on Abyss
- OR use `test_mode=true` to bypass API requirement

#### Issue 4: No Text Extracted
**Symptoms:** `ValueError: No readable text found in PDF`

**Solution:**
- PDF is likely image-based (scanned)
- Set `use_ocr=true` in environment variables
- Ensure tesseract-ocr is installed on Abyss platform

### 📊 Understanding the Logs

**Successful Run:**
```
INFO - File found successfully: /absolute/path/to/invoice.pdf
INFO - Extracted 1234 characters
INFO - Invoice parsed successfully
INFO - Found 5 line items
INFO - ✅ PROCESSING COMPLETE!
```

**Failed File Discovery:**
```
WARNING - File not found at: product_run/253/...pdf
INFO - Current working directory: /app/run
INFO - Files in current directory: ['run.py', 'requirements.txt', ...]
ERROR - File not found: PDF file not found: ...
```

### 🔄 What Changed in Code

**File:** `run.py`

**Added Function:** `find_invoice_file()`
- Tries multiple strategies to locate the uploaded file
- Returns valid path or original path (for clear error)

**Enhanced Logging:**
- Shows current directory
- Lists available files
- Confirms file location

**Why This Helps:**
- Handles Abyss platform file path quirks
- Provides debugging information
- Fallback strategies for file discovery

### 📞 If Issues Persist

1. **Check Abyss Documentation**
   - File upload behavior
   - Environment variable handling
   - Working directory structure

2. **Contact Abyss Support**
   - Provide full log output
   - Mention file path issue
   - Ask about correct file path format

3. **Test Locally First**
   ```bash
   export invoice_file=my_invoice.pdf
   export test_mode=true
   python run.py
   ```

4. **Report Issue**
   - If it's a widget bug, create GitHub issue
   - Include full logs
   - Include Abyss platform details

### ✅ Expected Behavior After Fix

**Before Fix:**
```
ERROR - File not found: product_run/253/68e2306d2038a/...pdf
```

**After Fix:**
```
INFO - Invoice file: invoice.pdf
INFO - File found successfully: /app/invoice.pdf
INFO - Extracted 1234 characters
✅ SUCCESS
```

---

## 📝 Notes for Abyss Deployment

1. **File Upload Handling**
   - Abyss may change file paths between versions
   - Widget now handles this automatically
   - No user configuration needed

2. **Environment Variables**
   - Set them in Abyss interface before test run
   - API keys are sensitive - use platform's secure storage
   - Optional variables have sensible defaults

3. **Output Directory**
   - Widget auto-creates `output/` directory
   - All files saved there
   - Abyss should return these to user

4. **Memory/CPU Limits**
   - Widget designed for ≤512MB RAM
   - Optimized for Abyss constraints
   - Large PDFs (>5MB) rejected automatically

---

**Last Updated:** 2025-10-05
**Widget Version:** 1.0.0
**Platform:** Abyss AI Widgets

