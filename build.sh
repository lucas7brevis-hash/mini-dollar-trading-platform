#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
sudo apt-get update && sudo apt-get install -y build-essential

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Ensure NLTK is installed before downloading data
pip install nltk

# Create NLTK data directory
mkdir -p nltk_data

# Download NLTK data to the created directory
python3 -m nltk.downloader -d nltk_data punkt vader_lexicon

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:.

# Create database tables
python3 init_db_render.py


