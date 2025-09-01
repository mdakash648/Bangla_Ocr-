#!/bin/bash

echo "Installing Bangla OCR Dependencies..."
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found! Please install Python 3.7 or higher first."
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

python3 --version

echo ""
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Dependencies installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Install Tesseract OCR:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-ben"
    echo "   macOS: brew install tesseract tesseract-lang"
    echo "2. Run test_installation.py to verify everything works"
    echo "3. Run the application with: python3 bangla_ocr_gui.py"
else
    echo ""
    echo "✗ Failed to install some dependencies."
    echo "Please check the error messages above."
fi

echo ""
read -p "Press Enter to continue..."
