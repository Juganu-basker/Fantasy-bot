#!/bin/bash

# Install dependencies if not already installed
pip3 install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload --port 8001
