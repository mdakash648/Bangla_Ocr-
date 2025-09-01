@echo off
:menu
cls
echo =====================================
echo         Bangla OCR Application
echo =====================================
echo 1. Run Bangla OCR GUI
echo 2. Instructions
echo 3. Exit
echo 4. Run Text File Combiner
echo =====================================
set /p choice=Enter your choice: 

if "%choice%"=="1" goto run_ocr
if "%choice%"=="2" goto instructions
if "%choice%"=="3" exit
if "%choice%"=="4" goto run_combiner
goto menu

:instructions
cls
echo Make sure you have:
echo 1. Python installed
echo 2. Required packages installed (pip install -r requirements.txt)
echo 3. Tesseract OCR installed
echo.
pause
goto menu

:run_ocr
cls
echo Starting Bangla OCR Application...
echo.
python bangla_ocr_gui.py
echo.
echo Application closed. Press any key to return to menu...
pause >nul
goto menu

:run_combiner
cls
echo Starting Text File Combiner...
echo.
python Text_file_combiner.py
echo.
echo Text File Combiner closed. Press any key to return to menu...
pause >nul
goto menu
