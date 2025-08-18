#!/usr/bin/env python3
"""
Script para corrigir o problema do banco de dados
"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importa os modelos na ordem correta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Cria uma nova instância do Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cria uma nova instância do SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

# Define os modelos diretamente aqui para evitar problemas de importação
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class CurrencyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(50), nullable=False)

class NewsData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    url = db.Column(db.Text)
    source = db.Column(db.String(100), nullable=False)
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False)

class TradingSignal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    signal_type = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    price_at_signal = db.Column(db.Float, nullable=False)
    reasoning = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

def fix_database():
    """Corrige o banco de dados criando todas as tabelas"""
    with app.app_context():
        print("Removendo banco de dados antigo...")
        
        # Remove o arquivo do banco se existir
        db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
        if os.path.exists(db_path):
            os.remove(db_path)
        
        print("Criando novo banco de dados...")
        
        # Cria todas as tabelas
        db.create_all()
        
        print("Banco de dados corrigido com sucesso!")
        print("Tabelas criadas:")
        print("- user")
        print("- currency_data")
        print("- news_data") 
        print("- trading_signal")

if __name__ == '__main__':
    fix_database()

