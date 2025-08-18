#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da plataforma Mini Dólar
"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import db
from src.models.financial_data import CurrencyData, NewsData, TradingSignal

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    with app.app_context():
        print("Criando tabelas do banco de dados...")
        
        # Remove todas as tabelas existentes
        db.drop_all()
        
        # Cria todas as tabelas
        db.create_all()
        
        print("Banco de dados inicializado com sucesso!")
        print("Tabelas criadas:")
        print("- user")
        print("- currency_data")
        print("- news_data")
        print("- trading_signal")

if __name__ == '__main__':
    init_database()

