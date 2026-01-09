#!/bin/sh

# Install system dependencies
apk add --no-cache \
    docker-cli \
    docker-compose \
    python3 \
    py3-pip \
    nodejs \
    npm \
    make \
    git \
    bash

# Install Python dependencies
pip install --break-system-packages \
    black \
    flake8 \
    pytest

# Install Node.js dependencies
npm install -g eslint

echo "Environment setup complete"
