#!/bin/bash

# Install system dependencies
apk add --no-cache python3 py3-pip nodejs npm

# Install Python dependencies
pip install --no-cache-dir --break-system-packages -r backend/requirements.txt

# Install Node.js dependencies (if needed)
cd frontend && npm install --no-optional
cd ..
