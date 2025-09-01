# বাংলা-ইংরেজি OCR সফটওয়্যার | Bengali-English OCR Software

A user-friendly GUI application for converting images to text with Bengali and English language support using Tesseract OCR.

## Features

- **Multi-language Support**: Bengali (বাংলা) and English text recognition
- **Multiple Input Options**: Single image, multiple images, or entire folder processing
- **User-friendly Interface**: Modern GUI with progress tracking and results display
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Settings Persistence**: Remembers your preferences and Tesseract configuration

## Prerequisites

### 1. Python Requirements
- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - Pillow (PIL)
  - pytesseract
  - tkinter (usually comes with Python)

### 2. Tesseract OCR Installation

#### Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Choose the latest version (e.g., tesseract-ocr-w64-setup-5.3.1.20230401.exe)
3. During installation, make sure to:
   - Check "Additional language data (download)"
   - Check "Bengali" language support
   - Add Tesseract to system PATH
4. Restart your computer after installation

#### Alternative Windows Installation:
```bash
# Using Chocolatey
choco install tesseract

# Using winget
winget install UB-Mannheim.TesseractOCR
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ben
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

## Installation

1. **Clone or download** this project to your local machine
2. **Navigate** to the project directory:
   ```bash
   cd Bangla_Ocr
   ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Verify Tesseract installation**:
   ```bash
   tesseract --version
   ```

## Usage

1. **Run the application**:
   ```bash
   python bangla_ocr_gui.py
   ```

2. **Configure Tesseract** (if not auto-detected):
   - Click "Settings" button
   - Browse to your `tesseract.exe` location
   - Test the configuration
   - Save settings

3. **Select Input**:
   - **Single Image**: Browse for one image file
   - **Multiple Images**: Select multiple image files
   - **Image Folder**: Choose a folder containing images

4. **Configure Output**:
   - Select output folder for text files
   - Choose languages (Bengali, English, or both)

5. **Start Processing**:
   - Click "Start OCR Processing"
   - Monitor progress in real-time
   - View results in the text area

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Output

- Text files (.txt) with the same name as input images
- UTF-8 encoding for proper Bengali text support
- Results displayed in the application interface

## Troubleshooting

### Tesseract Not Found
- Ensure Tesseract is properly installed
- Use the Settings dialog to configure the correct path
- Restart the application after configuration

### Bengali Text Not Recognized
- Verify Bengali language pack is installed with Tesseract
- Check that the image quality is sufficient
- Ensure proper lighting and contrast in the original image

### Performance Issues
- Process images in smaller batches
- Use higher quality images for better accuracy
- Close other applications to free up system resources

## File Structure

```
Bangla_Ocr/
├── bangla_ocr_gui.py    # Main application file
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── ocr_settings.json    # Application settings (created automatically)
```

## Technical Details

- **GUI Framework**: Tkinter with ttk styling
- **OCR Engine**: Tesseract via pytesseract
- **Image Processing**: PIL (Pillow)
- **Threading**: Background processing for responsive UI
- **Settings**: JSON-based configuration storage

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify Tesseract installation
3. Check Python package versions
4. Review error messages in the application

---

**Note**: This application requires Tesseract OCR to be installed on your system. The application will guide you through the configuration process if Tesseract is not automatically detected.
