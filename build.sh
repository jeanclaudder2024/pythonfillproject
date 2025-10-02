#!/bin/bash

# Install Python dependencies first
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Try to install system dependencies (may fail on some platforms)
echo "Attempting to install system dependencies..."

# Update package list
apt-get update || echo "apt-get update failed, continuing..."

# Install LibreOffice for DOCX to PDF conversion
apt-get install -y libreoffice-writer-nogui libreoffice-core || echo "LibreOffice installation failed, continuing..."

# Install unoconv as alternative
apt-get install -y unoconv || echo "unoconv installation failed, continuing..."

# Install pandoc as another alternative
apt-get install -y pandoc || echo "pandoc installation failed, continuing..."

echo "Build completed successfully!"
