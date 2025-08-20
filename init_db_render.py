import os
import sys

# Adiciona o diretório pai ao sys.path para que src seja encontrado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from main import app, db
from models.user import User
from models.financial_data import CurrencyData, NewsData, TradingSignal

with app.app_context():
    db.create_all()
    print('Database tables created successfully!')


