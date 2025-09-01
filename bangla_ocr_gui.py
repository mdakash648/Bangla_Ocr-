#!/usr/bin/env python3
"""
Bengali-English OCR GUI Application
A user-friendly interface for converting images to text with Bengali and English language support
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from PIL import Image, ImageTk
import pytesseract
from pathlib import Path
import json
import webbrowser
import sys
import shutil
import platform

class BanglaOCRGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("বাংলা-ইংরেজি OCR সফটওয়্যার | Bengali-English OCR Software")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.input_files = []
        self.output_folder = ""
        self.is_processing = False
        self.tesseract_available = False
        self.tesseract_path = None
        
        # Load settings (may include tesseract path), then check availability
        self.load_settings()
        self.check_tesseract()
        
        # Configure style
        self.setup_styles()
        
        # Create GUI
        self.create_widgets()

        # Load settings again to populate UI-bound values like output folder
        self.load_settings()

        # If Tesseract isn't available, prompt configuration dialog
        if not self.tesseract_available:
            # Delay a bit to let main window show up
            self.root.after(300, self.show_tesseract_config_dialog)
    
    def check_tesseract(self):
        """Check and attempt to configure Tesseract availability."""
        # 1) If we have a saved/explicit path, try that first
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            if self._test_tesseract_cmd(self.tesseract_path):
                self.tesseract_available = True
                return

        # 2) Env overrides
        env_candidates = [
            os.environ.get('TESSERACT_CMD'),
            os.environ.get('TESSERACT_PATH'),
        ]
        for cand in env_candidates:
            if cand:
                if self._test_tesseract_cmd(cand):
                    self._set_tesseract_cmd(cand, persist=False)
                    self.tesseract_available = True
                    return

        # 3) PATH discovery
        which_path = shutil.which('tesseract')
        if which_path and self._test_tesseract_cmd(which_path):
            self._set_tesseract_cmd(which_path, persist=False)
            self.tesseract_available = True
            return

        # 4) Common Windows install locations
        if platform.system().lower().startswith('win'):
            candidates = self._common_windows_paths()
            for cand in candidates:
                if os.path.isfile(cand) and self._test_tesseract_cmd(cand):
                    self._set_tesseract_cmd(cand, persist=False)
                    self.tesseract_available = True
                    return

        # 5) Final fallback: try default pytesseract behavior
        try:
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except Exception:
            self.tesseract_available = False

    def _common_windows_paths(self):
        pf = os.environ.get('PROGRAMFILES', r"C:\\Program Files")
        pf86 = os.environ.get('PROGRAMFILES(X86)', r"C:\\Program Files (x86)")
        localapp = os.environ.get('LOCALAPPDATA', os.path.expanduser(r"~\\AppData\\Local"))
        candidates = [
            os.path.join(pf, 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(pf86, 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(localapp, 'Programs', 'Tesseract-OCR', 'tesseract.exe'),
        ]
        return candidates

    def _test_tesseract_cmd(self, path_candidate):
        """Return True if path_candidate works for pytesseract."""
        try:
            if not path_candidate:
                return False
            pytesseract.pytesseract.tesseract_cmd = path_candidate
            _ = pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _set_tesseract_cmd(self, path_value, persist=True):
        """Set tesseract command, optionally persisting to settings."""
        self.tesseract_path = path_value
        pytesseract.pytesseract.tesseract_cmd = path_value
        if persist:
            self.save_settings()
    
    def setup_styles(self):
        """Configure modern styling for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'), 
                       foreground='#2c3e50',
                       background='#f0f0f0')
        
        style.configure('Header.TLabel', 
                       font=('Arial', 12, 'bold'), 
                       foreground='#34495e',
                       background='#f0f0f0')
        
        style.configure('Success.TLabel', 
                       font=('Arial', 10), 
                       foreground='#27ae60',
                       background='#f0f0f0')
        
        style.configure('Error.TLabel', 
                       font=('Arial', 10), 
                       foreground='#e74c3c',
                       background='#f0f0f0')
        
        style.configure('Warning.TLabel', 
                       font=('Arial', 10, 'bold'), 
                       foreground='#f39c12',
                       background='#f0f0f0')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="বাংলা-ইংরেজি OCR সফটওয়্যার", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, 
                                   text="Bengali-English OCR Software", 
                                   style='Header.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 30))
        
        # Tesseract Status Warning
        if not self.tesseract_available:
            warning_frame = ttk.Frame(main_frame)
            warning_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
            warning_frame.columnconfigure(0, weight=1)
            
            warning_label = ttk.Label(warning_frame, 
                                     text="⚠ Tesseract OCR is not installed!", 
                                     style='Warning.TLabel')
            warning_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
            
            install_label = ttk.Label(warning_frame, 
                                     text="Please install Tesseract OCR to use this application.", 
                                     style='Error.TLabel')
            install_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
            
            install_btn = ttk.Button(warning_frame, text="Install Instructions", 
                                    command=self.show_install_instructions)
            install_btn.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

            # Config button
            cfg_btn = ttk.Button(warning_frame, text="Configure Tesseract...", 
                                 command=self.show_tesseract_config_dialog)
            cfg_btn.grid(row=2, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))
            
            # Disable processing if Tesseract not available
            self.create_disabled_widgets(main_frame)
            return
        
        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Input Images", padding="15")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # Single image selection
        ttk.Label(input_frame, text="Single Image:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.single_image_var = tk.StringVar()
        single_entry = ttk.Entry(input_frame, textvariable=self.single_image_var, width=50)
        single_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_single_image).grid(row=0, column=2, pady=(0, 5))
        
        # Multiple images selection
        ttk.Label(input_frame, text="Multiple Images:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.multiple_images_var = tk.StringVar()
        multiple_entry = ttk.Entry(input_frame, textvariable=self.multiple_images_var, width=50)
        multiple_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(10, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_multiple_images).grid(row=1, column=2, pady=(10, 5))
        
        # Folder selection
        ttk.Label(input_frame, text="Image Folder:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(input_frame, textvariable=self.folder_var, width=50)
        folder_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(10, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_folder).grid(row=2, column=2, pady=(10, 5))
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="15")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Folder:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=2, pady=(0, 5))
        
        # Language options
        lang_frame = ttk.Frame(output_frame)
        lang_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(lang_frame, text="Languages:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.bengali_var = tk.BooleanVar(value=True)
        self.english_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(lang_frame, text="বাংলা (Bengali)", variable=self.bengali_var).grid(row=0, column=1, padx=(20, 0))
        ttk.Checkbutton(lang_frame, text="English", variable=self.english_var).grid(row=0, column=2, padx=(20, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))
        
        self.process_btn = ttk.Button(button_frame, text="Start OCR Processing", 
                                     command=self.start_processing)
        self.process_btn.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Settings", command=self.show_settings).grid(row=0, column=2)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="15")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to process")
        ttk.Label(progress_frame, textvariable=self.progress_var, style='Success.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="15")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure main frame row weights
        main_frame.rowconfigure(6, weight=1)
    
    def create_disabled_widgets(self, main_frame):
        """Create disabled widgets when Tesseract is not available"""
        # Disabled input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Images (Disabled - Tesseract Required)", padding="15")
        input_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Single Image:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        single_entry = ttk.Entry(input_frame, state='disabled', width=50)
        single_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 5))
        ttk.Button(input_frame, text="Browse", state='disabled').grid(row=0, column=2, pady=(0, 5))
        
        # Disabled output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings (Disabled - Tesseract Required)", padding="15")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output Folder:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        output_entry = ttk.Entry(output_frame, state='disabled', width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 5))
        ttk.Button(output_frame, text="Browse", state='disabled').grid(row=0, column=2, pady=(0, 5))
        
        # Disabled control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Button(button_frame, text="Start OCR Processing", state='disabled').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", state='disabled').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Settings", command=self.show_settings).grid(row=0, column=2)
        
        # Disabled progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress (Disabled - Tesseract Required)", padding="15")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        ttk.Label(progress_frame, text="Tesseract OCR not available", style='Error.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Disabled results section
        results_frame = ttk.LabelFrame(main_frame, text="Results (Disabled - Tesseract Required)", padding="15")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80, state='disabled')
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Tesseract OCR not available")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure main frame row weights
        main_frame.rowconfigure(7, weight=1)
    
    def show_install_instructions(self):
        """Show installation instructions for Tesseract"""
        instructions = """Tesseract OCR Installation Instructions:

Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Choose the latest version (e.g., tesseract-ocr-w64-setup-5.3.1.20230401.exe)
3. During installation, make sure to:
   - Check "Additional language data (download)"
   - Check "Bengali" language support
   - Add Tesseract to system PATH
4. Restart your computer after installation

Alternative Windows Installation:
1. Use Chocolatey: choco install tesseract
2. Use winget: winget install UB-Mannheim.TesseractOCR

Linux (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ben

macOS:
brew install tesseract tesseract-lang

After installation:
1. Restart this application
2. Verify Tesseract is working by running: tesseract --version

Note: Bengali language support is required for Bengali text recognition."""
        
        # Create instructions window
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Tesseract Installation Instructions")
        instructions_window.geometry("600x500")
        instructions_window.transient(self.root)
        instructions_window.grab_set()
        
        # Instructions content
        ttk.Label(instructions_window, text="Installation Instructions", style='Title.TLabel').pack(pady=20)
        
        text_widget = scrolledtext.ScrolledText(instructions_window, height=20, width=70)
        text_widget.pack(padx=20, pady=(0, 20))
        text_widget.insert(tk.END, instructions)
        text_widget.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(instructions_window)
        button_frame.pack(pady=(0, 20))
        
        ttk.Button(button_frame, text="Download Windows Version", 
                   command=lambda: webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Close", 
                   command=instructions_window.destroy).pack(side=tk.LEFT)
    
    def browse_single_image(self):
        """Browse for a single image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.single_image_var.set(file_path)
            self.folder_var.set("")
            self.multiple_images_var.set("")
    
    def browse_multiple_images(self):
        """Browse for multiple image files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Image Files",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("All files", "*.*")
            ]
        )
        if file_paths:
            self.multiple_images_var.set("; ".join(file_paths))
            self.single_image_var.set("")
            self.folder_var.set("")
    
    def browse_folder(self):
        """Browse for a folder containing images"""
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if folder_path:
            self.folder_var.set(folder_path)
            self.single_image_var.set("")
            self.multiple_images_var.set("")
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_var.set(folder_path)
    
    def get_input_files(self):
        """Get list of input files based on user selection"""
        files = []
        
        # Single image
        if self.single_image_var.get():
            files.append(self.single_image_var.get())
        
        # Multiple images
        if self.multiple_images_var.get():
            files.extend([f.strip() for f in self.multiple_images_var.get().split(";")])
        
        # Folder
        if self.folder_var.get():
            folder_path = self.folder_var.get()
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']:
                files.extend(Path(folder_path).glob(ext))
            files = [str(f) for f in files]
        
        return list(set(files))  # Remove duplicates
    
    def get_language_config(self):
        """Get language configuration for OCR"""
        languages = []
        if self.bengali_var.get():
            languages.append('ben')
        if self.english_var.get():
            languages.append('eng')
        
        if not languages:
            languages = ['ben', 'eng']  # Default to both
        
        return '+'.join(languages)
    
    def start_processing(self):
        """Start OCR processing in a separate thread"""
        if self.is_processing or not self.tesseract_available:
            return
        
        # Validate inputs
        input_files = self.get_input_files()
        if not input_files:
            messagebox.showerror("Error", "Please select at least one input image or folder.")
            return
        
        if not self.output_var.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return
        
        # Create output folder if it doesn't exist
        os.makedirs(self.output_var.get(), exist_ok=True)
        
        # Start processing in background
        self.is_processing = True
        self.process_btn.config(state='disabled')
        self.progress_var.set("Processing...")
        self.status_var.set("Processing images...")
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = threading.Thread(target=self.process_images, args=(input_files,))
        thread.daemon = True
        thread.start()
    
    def process_images(self, input_files):
        """Process images with OCR"""
        try:
            total_files = len(input_files)
            success_count = 0
            language_config = self.get_language_config()
            
            self.root.after(0, lambda: self.progress_bar.config(maximum=total_files))
            
            for i, file_path in enumerate(input_files):
                try:
                    # Update progress
                    self.root.after(0, lambda f=file_path: self.progress_var.set(f"Processing: {os.path.basename(f)}"))
                    self.root.after(0, lambda x=i+1: self.progress_bar.config(value=x))
                    
                    # Process image
                    if self.process_single_image(file_path, language_config):
                        success_count += 1
                        self.root.after(0, lambda f=file_path: self.add_result(f"✓ Success: {os.path.basename(f)}"))
                    else:
                        self.root.after(0, lambda f=file_path: self.add_result(f"✗ Failed: {os.path.basename(f)}"))
                    
                except Exception as e:
                    self.root.after(0, lambda f=file_path, e=str(e): self.add_result(f"✗ Error: {os.path.basename(f)} - {e}"))
            
            # Processing complete
            self.root.after(0, lambda: self.processing_complete(success_count, total_files))
            
        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))
    
    def process_single_image(self, image_path, language_config):
        """Process a single image with OCR"""
        try:
            # Open image
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=language_config)
            
            # Create output filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_file = os.path.join(self.output_var.get(), f"{base_name}.txt")
            
            # Save text to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return False
    
    def add_result(self, message):
        """Add result message to results text area"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
    
    def processing_complete(self, success_count, total_count):
        """Handle processing completion"""
        self.is_processing = False
        self.process_btn.config(state='normal')
        self.progress_var.set(f"Completed! {success_count}/{total_count} images processed successfully.")
        self.status_var.set(f"Completed - {success_count}/{total_count} successful")
        
        messagebox.showinfo("Processing Complete", 
                           f"OCR processing completed!\n\n"
                           f"Successfully processed: {success_count}/{total_count} images\n"
                           f"Output saved to: {self.output_var.get()}")
    
    def processing_error(self, error_message):
        """Handle processing error"""
        self.is_processing = False
        self.process_btn.config(state='normal')
        self.progress_var.set("Error occurred during processing")
        self.status_var.set("Error")
        
        messagebox.showerror("Processing Error", f"An error occurred:\n{error_message}")
    
    def clear_all(self):
        """Clear all input fields and results"""
        self.single_image_var.set("")
        self.multiple_images_var.set("")
        self.folder_var.set("")
        self.output_var.set("")
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set("Ready to process")
        self.status_var.set("Ready")
        self.progress_bar.config(value=0)
    
    def show_settings(self):
        """Show settings dialog (includes Tesseract config)."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("OCR Settings")
        settings_window.geometry("520x360")
        settings_window.transient(self.root)
        settings_window.grab_set()

        container = ttk.Frame(settings_window, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="OCR Settings", style='Title.TLabel').grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky=tk.W)

        # Tesseract Path Section
        ttk.Label(container, text="Tesseract Executable:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W)
        tess_var = tk.StringVar(value=self.tesseract_path or pytesseract.pytesseract.tesseract_cmd)
        tess_entry = ttk.Entry(container, textvariable=tess_var, width=50)
        tess_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 5))

        def browse_tesseract():
            filetypes = [("Tesseract Executable", "tesseract.exe"), ("All files", "*.*")]
            initial = os.path.dirname(tess_var.get()) if tess_var.get() else None
            path = filedialog.askopenfilename(title="Select tesseract.exe", filetypes=filetypes, initialdir=initial)
            if path:
                tess_var.set(path)

        def autodetect_tesseract():
            # Try current detection routine
            # Save current to restore if needed
            orig = pytesseract.pytesseract.tesseract_cmd
            self.check_tesseract()
            if self.tesseract_available and pytesseract.pytesseract.tesseract_cmd:
                tess_var.set(pytesseract.pytesseract.tesseract_cmd)
                status_var.set("Detected working Tesseract.")
            else:
                pytesseract.pytesseract.tesseract_cmd = orig
                status_var.set("Auto-detect failed. Please browse manually.")

        def test_tesseract():
            candidate = tess_var.get().strip()
            if self._test_tesseract_cmd(candidate):
                status_var.set("Tesseract OK ✔")
            else:
                status_var.set("Tesseract not working ✖. Check the path.")

        def save_tesseract():
            candidate = tess_var.get().strip()
            if not candidate:
                messagebox.showerror("Invalid Path", "Please provide a path to tesseract.exe")
                return
            if not os.path.isfile(candidate):
                messagebox.showerror("Invalid Path", "Selected path does not exist or is not a file.")
                return
            if not self._test_tesseract_cmd(candidate):
                if not messagebox.askyesno("Path Not Verified", "The selected path could not be verified. Save anyway?"):
                    return
            self._set_tesseract_cmd(candidate, persist=True)
            self.tesseract_available = self._test_tesseract_cmd(candidate)
            status_var.set("Saved. Restart not required.")
            # Rebuild UI to enable controls if now available
            self._rebuild_ui()

        ttk.Button(container, text="Browse...", command=browse_tesseract).grid(row=2, column=2, padx=(8, 0), sticky=tk.W)
        btns_row = ttk.Frame(container)
        btns_row.grid(row=3, column=0, columnspan=3, pady=(8, 8), sticky=tk.W)
        ttk.Button(btns_row, text="Auto-Detect", command=autodetect_tesseract).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns_row, text="Test", command=test_tesseract).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btns_row, text="Save", command=save_tesseract).grid(row=0, column=2)

        status_var = tk.StringVar(value="")
        ttk.Label(container, textvariable=status_var, style='Success.TLabel').grid(row=4, column=0, columnspan=3, sticky=tk.W)

        # About section
        ttk.Label(container, text="About", style='Header.TLabel').grid(row=5, column=0, pady=(20, 5), sticky=tk.W)
        ttk.Label(container, text=(
            "Bengali-English OCR Software\n"
            "Version 1.1\n\n"
            "Works without system PATH by configuring the Tesseract path."
        )).grid(row=6, column=0, columnspan=3, sticky=tk.W)

        # Close button
        ttk.Button(container, text="Close", command=settings_window.destroy).grid(row=7, column=0, pady=(20,0), sticky=tk.W)

    def show_tesseract_config_dialog(self):
        """Dedicated Tesseract configuration dialog, also accessible on startup."""
        # Reuse show_settings for unified experience
        self.show_settings()
    
    def load_settings(self):
        """Load application settings"""
        try:
            if os.path.exists('ocr_settings.json'):
                with open('ocr_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'output_folder' in settings:
                        self.output_var.set(settings['output_folder'])
                    if 'tesseract_path' in settings and settings['tesseract_path']:
                        self.tesseract_path = settings['tesseract_path']
                        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        except Exception:
            pass
    
    def save_settings(self):
        """Save application settings"""
        try:
            settings = {}
            # Load existing to merge
            if os.path.exists('ocr_settings.json'):
                try:
                    with open('ocr_settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f) or {}
                except Exception:
                    settings = {}
            # Update values
            settings['output_folder'] = self.output_var.get()
            if self.tesseract_path:
                settings['tesseract_path'] = self.tesseract_path
            with open('ocr_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _rebuild_ui(self):
        """Rebuild main UI to reflect Tesseract availability changes."""
        # Re-check availability
        self.check_tesseract()
        # Destroy all widgets and recreate
        for child in list(self.root.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass
        self.create_widgets()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = BanglaOCRGUI(root)
    
    # Save settings on close
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
