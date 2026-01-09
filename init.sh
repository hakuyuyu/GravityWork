#!/bin/bash

# Install system dependencies
apk add --no-cache nodejs npm python3 py3-pip

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn python-dotenv qdrant-client pytest

# Install Node.js dependencies
cd frontend
npm install
cd ..
