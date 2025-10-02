#!/bin/bash

# Install system dependencies for PDF conversion
echo "Installing system dependencies..."

# Update package list
apt-get update

# Install LibreOffice for DOCX to PDF conversion
apt-get install -y libreoffice-writer-nogui libreoffice-core

# Install unoconv as alternative
apt-get install -y unoconv

# Install pandoc as another alternative
apt-get install -y pandoc

# Install additional dependencies
apt-get install -y fonts-liberation

echo "System dependencies installed successfully!"

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!"
