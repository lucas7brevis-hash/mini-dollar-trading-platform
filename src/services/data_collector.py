import requests
import yfinance as yf
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataCollector:
    """Coleta dados financeiros de várias fontes gratuitas"""
    
    def __init__(self):
        self.alpha_vantage_key = None  # Será configurado pelo usuário
        self.session = requests.Session()
        
    def get_usd_brl_rate(self) -> Optional[Dict]:
        """Obtém a cotação USD/BRL usando múltiplas fontes"""
        
        # Tenta primeiro com yfinance
        try:
            ticker = yf.Ticker("USDBRL=X")
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                latest_price = data['Close'].iloc[-1]
                return {
                    'symbol': 'USD/BRL',
                    'price': float(latest_price),
                    'timestamp': datetime.now(),
                    'source': 'yfinance'
                }
        except Exception as e:
            logger.warning(f"Erro ao obter dados do yfinance: {e}")
        
        # Fallback para API gratuita de câmbio
        try:
            response = self.session.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                brl_rate = data['rates'].get('BRL')
                if brl_rate:
                    return {
                        'symbol': 'USD/BRL',
                        'price': float(brl_rate),
                        'timestamp': datetime.now(),
                        'source': 'exchangerate-api'
                    }
        except Exception as e:
            logger.warning(f"Erro ao obter dados da exchangerate-api: {e}")
        
        # Fallback para FreeCurrencyAPI
        try:
            response = self.session.get(
                "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_YOUR_API_KEY&currencies=BRL&base_currency=USD",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                brl_rate = data['data'].get('BRL')
                if brl_rate:
                    return {
                        'symbol': 'USD/BRL',
                        'price': float(brl_rate),
                        'timestamp': datetime.now(),
                        'source': 'freecurrencyapi'
                    }
        except Exception as e:
            logger.warning(f"Erro ao obter dados da freecurrencyapi: {e}")
        
        return None
    
    def get_alpha_vantage_forex(self) -> Optional[Dict]:
        """Obtém dados de forex da Alpha Vantage (se API key disponível)"""
        if not self.alpha_vantage_key:
            return None
            
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': 'USD',
                'to_symbol': 'BRL',
                'interval': '5min',
                'apikey': self.alpha_vantage_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                time_series = data.get('Time Series FX (5min)', {})
                if time_series:
                    latest_time = max(time_series.keys())
                    latest_data = time_series[latest_time]
                    return {
                        'symbol': 'USD/BRL',
                        'price': float(latest_data['4. close']),
                        'timestamp': datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S'),
                        'source': 'alpha_vantage'
                    }
        except Exception as e:
            logger.warning(f"Erro ao obter dados da Alpha Vantage: {e}")
        
        return None
    
    def get_twelve_data_forex(self) -> Optional[Dict]:
        """Obtém dados de forex da Twelve Data (plano gratuito limitado)"""
        try:
            # Usando endpoint gratuito da Twelve Data
            url = "https://api.twelvedata.com/price"
            params = {
                'symbol': 'USD/BRL',
                'apikey': 'demo'  # Chave demo limitada
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    return {
                        'symbol': 'USD/BRL',
                        'price': float(data['price']),
                        'timestamp': datetime.now(),
                        'source': 'twelve_data'
                    }
        except Exception as e:
            logger.warning(f"Erro ao obter dados da Twelve Data: {e}")
        
        return None
    
    def get_current_rate(self) -> Optional[Dict]:
        """Obtém a cotação atual usando a melhor fonte disponível"""
        
        # Tenta as fontes em ordem de preferência
        sources = [
            self.get_usd_brl_rate,
            self.get_alpha_vantage_forex,
            self.get_twelve_data_forex
        ]
        
        for source_func in sources:
            try:
                result = source_func()
                if result:
                    logger.info(f"Dados obtidos de {result['source']}: {result['price']}")
                    return result
            except Exception as e:
                logger.warning(f"Erro na fonte {source_func.__name__}: {e}")
                continue
        
        logger.error("Não foi possível obter dados de nenhuma fonte")
        return None
    
    def get_historical_data(self, days: int = 30) -> List[Dict]:
        """Obtém dados históricos do USD/BRL"""
        try:
            ticker = yf.Ticker("USDBRL=X")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = ticker.history(start=start_date, end=end_date)
            
            historical_data = []
            for date, row in data.iterrows():
                historical_data.append({
                    'symbol': 'USD/BRL',
                    'price': float(row['Close']),
                    'timestamp': date,
                    'source': 'yfinance_historical'
                })
            
            return historical_data
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos: {e}")
            return []
    
    def set_alpha_vantage_key(self, api_key: str):
        """Define a chave da API Alpha Vantage"""
        self.alpha_vantage_key = api_key
        logger.info("Chave Alpha Vantage configurada")

# Instância global do coletor
data_collector = FinancialDataCollector()

