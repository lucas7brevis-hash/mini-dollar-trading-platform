#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
sudo apt-get update && sudo apt-get install -y build-essential

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data for sentiment analysis
python3 -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:.

# Create database tables
python3 -c "\
import os\
import sys\
from src.main import app\
from src.models.user import db\
from src.models.financial_data import CurrencyData, NewsData, TradingSignal\
\
with app.app_context():\
    db.create_all()\
    print(\'Database tables created successfully!\')\
"

