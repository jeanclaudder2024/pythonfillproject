#!/usr/bin/env python3
"""
Test LibreOffice PDF conversion locally
"""

import os
import subprocess
from pathlib import Path

def test_libreoffice_conversion():
    """Test LibreOffice PDF conversion"""
    print("Testing LibreOffice PDF conversion...")
    
    # Check if LibreOffice is installed
    try:
        if os.name == 'nt':  # Windows
            cmd = ['C:\\Program Files\\LibreOffice\\program\\soffice.exe', '--version']
        else:  # Linux/Mac
            cmd = ['libreoffice', '--version']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"LibreOffice is installed: {result.stdout.strip()}")
        else:
            print("LibreOffice is not installed or not working")
            return False
    except Exception as e:
        print(f"Error checking LibreOffice: {e}")
        return False
    
    # Test conversion with a sample document
    try:
        # Check if we have a template file
        template_dir = Path("fixed_templates")
        if not template_dir.exists():
            print("fixed_templates directory not found")
            return False
        
        template_files = list(template_dir.glob("*.docx"))
        if not template_files:
            print("No .docx template files found in fixed_templates directory")
            return False
        
        # Use the first template for testing
        test_template = template_files[0]
        print(f"Testing with template: {test_template}")
        
        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Test conversion
        output_pdf = output_dir / f"test_{test_template.stem}.pdf"
        
        if os.name == 'nt':  # Windows
            cmd = [
                'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(test_template)
            ]
        else:  # Linux/Mac
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(test_template)
            ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            expected_pdf = output_dir / f"{test_template.stem}.pdf"
            if expected_pdf.exists():
                print(f"PDF conversion successful: {expected_pdf}")
                print(f"File size: {expected_pdf.stat().st_size} bytes")
                return True
            else:
                print(f"Expected PDF file not found: {expected_pdf}")
                return False
        else:
            print(f"LibreOffice conversion failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("LibreOffice conversion timed out")
        return False
    except Exception as e:
        print(f"Error during conversion test: {e}")
        return False

if __name__ == "__main__":
    print("LibreOffice PDF Conversion Test")
    print("=" * 50)
    
    success = test_libreoffice_conversion()
    
    print("=" * 50)
    if success:
        print("LibreOffice test PASSED! Ready for deployment.")
    else:
        print("LibreOffice test FAILED! Please install LibreOffice first.")
        print("\nTo install LibreOffice:")
        print("Windows: Download from https://www.libreoffice.org/download/download/")
        print("Linux: sudo apt-get install libreoffice-writer libreoffice-calc")
        print("Mac: brew install --cask libreoffice")