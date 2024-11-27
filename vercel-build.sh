#!/bin/bash

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build
