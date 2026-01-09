#!/bin/bash

# Install system dependencies
apk add --no-cache nodejs npm python3 py3-pip

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn python-dotenv qdrant-client pytest httpx

# Install Node.js dependencies
cd frontend
npm install
cd ..
