#!/bin/bash

echo "Starting Bangla OCR Application..."
echo ""
echo "Make sure you have:"
echo "1. Python installed"
echo "2. Required packages installed (pip install -r requirements.txt)"
echo "3. Tesseract OCR installed"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check if required packages are installed
if ! python3 -c "import PIL, pytesseract" &> /dev/null; then
    echo "Required packages not found. Installing..."
    pip3 install -r requirements.txt
fi

echo "Starting application..."
python3 bangla_ocr_gui.py

echo ""
echo "Application closed."
