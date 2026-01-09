#!/bin/bash

# Install system dependencies
apk add --no-cache python3 py3-pip nodejs npm

# Install Python dependencies
pip install PyPDF2 python-docx

# Install Node.js dependencies
cd frontend && npm install && cd ..

echo "Environment initialized successfully"
