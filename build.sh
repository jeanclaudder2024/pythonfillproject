#!/bin/bash

# Install system dependencies for docx2pdf
apt-get update
apt-get install -y libreoffice

# Install Python dependencies
pip install -r requirements.txt
