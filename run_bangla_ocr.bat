@echo off
echo Starting Bangla OCR Application...
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Required packages installed (pip install -r requirements.txt)
echo 3. Tesseract OCR installed
echo.
echo Press any key to continue...
pause >nul

python bangla_ocr_gui.py

echo.
echo Application closed. Press any key to exit...
pause >nul
