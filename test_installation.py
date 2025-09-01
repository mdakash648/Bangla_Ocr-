#!/usr/bin/env python3
"""
Test script to verify Bangla OCR application installation
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(module_name)
            print(f"✓ {package_name} imported successfully")
            return True
        else:
            importlib.import_module(module_name)
            print(f"✓ {module_name} imported successfully")
            return True
    except ImportError as e:
        print(f"✗ {module_name} import failed: {e}")
        return False

def test_tesseract():
    """Test Tesseract availability"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"✗ Tesseract test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Bangla OCR Installation Test")
    print("=" * 40)
    
    # Test Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"✗ Python version {python_version.major}.{python_version.minor} is too old. Need 3.7+")
        return False
    
    print("\nTesting required modules:")
    
    # Test required modules
    modules = [
        ("tkinter", "Tkinter GUI framework"),
        ("PIL", "Pillow (PIL) image processing"),
        ("pytesseract", "Pytesseract OCR wrapper"),
        ("pathlib", "Pathlib file operations"),
        ("json", "JSON data handling"),
        ("threading", "Threading support"),
        ("os", "Operating system interface")
    ]
    
    all_modules_ok = True
    for module, description in modules:
        if not test_import(module, description):
            all_modules_ok = False
    
    print("\nTesting Tesseract OCR:")
    tesseract_ok = test_tesseract()
    
    print("\n" + "=" * 40)
    if all_modules_ok and tesseract_ok:
        print("✓ All tests passed! Your installation is ready.")
        print("\nYou can now run the application with:")
        print("  python bangla_ocr_gui.py")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        if not all_modules_ok:
            print("\nTo install missing Python packages, run:")
            print("  pip install -r requirements.txt")
        if not tesseract_ok:
            print("\nTo install Tesseract OCR:")
            print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-ben")
            print("  macOS: brew install tesseract tesseract-lang")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
