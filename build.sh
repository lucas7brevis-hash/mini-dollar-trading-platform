#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data for sentiment analysis
python -c "import nltk; nltk.download(\'punkt\'); nltk.download(\'vader_lexicon\')"

# Create database tables
python -c "
import os
import sys
sys.path.insert(0, os.getcwd())
from src.main import app
from src.models.user import db
from src.models.financial_data import CurrencyData, NewsData, TradingSignal

with app.app_context():
    db.create_all()
    print(\'Database tables created successfully!\')
"

