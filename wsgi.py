#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment
"""

import sys
import os
from pathlib import Path

# Add project directory to Python path
project_home = '/home/yourusername/autofill'  # Replace 'yourusername' with your PythonAnywhere username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set up environment
os.environ.setdefault('PYTHONPATH', project_home)

# Import the FastAPI app
from working_fastapi import app as application

if __name__ == "__main__":
    application.run()
