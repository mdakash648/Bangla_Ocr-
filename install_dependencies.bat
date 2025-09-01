@echo off
echo Installing Bangla OCR Dependencies...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.7 or higher first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing required Python packages...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✓ Dependencies installed successfully!
    echo.
    echo Next steps:
    echo 1. Install Tesseract OCR (see README.md for instructions)
    echo 2. Run test_installation.py to verify everything works
    echo 3. Run the application with: python bangla_ocr_gui.py
) else (
    echo.
    echo ✗ Failed to install some dependencies.
    echo Please check the error messages above.
)

echo.
pause
