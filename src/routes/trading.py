from flask import Blueprint, jsonify, request
from src.services.trading_algorithm import trading_algorithm
from src.services.data_collector import data_collector
from src.services.sentiment_analyzer import sentiment_analyzer
from src.main import db
from src.models.financial_data import CurrencyData, NewsData, TradingSignal
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/generate-signal', methods=['POST'])
def generate_trading_signal():
    """Gera sinal de trading avançado baseado em análise técnica e sentimento"""
    try:
        # Parâmetros da requisição
        data = request.get_json() or {}
        hours_back = data.get('hours_back', 24)
        min_price_points = data.get('min_price_points', 20)
        
        # Obtém cotação atual
        current_rate = data_collector.get_current_rate()
        if not current_rate:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter cotação atual'
            }), 500
        
        # Obtém dados históricos de preço
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        price_query = CurrencyData.query.filter(
            CurrencyData.timestamp >= cutoff_time
        ).order_by(CurrencyData.timestamp.asc()).all()
        
        price_data = [
            {
                'price': record.price,
                'timestamp': record.timestamp,
                'source': record.source
            }
            for record in price_query
        ]
        
        # Se não há dados suficientes, usa dados históricos do yfinance
        if len(price_data) < min_price_points:
            logger.info("Poucos dados no banco, buscando dados históricos...")
            historical_data = data_collector.get_historical_data(days=7)
            if historical_data:
                price_data.extend(historical_data)
                # Remove duplicatas e ordena
                seen_timestamps = set()
                unique_data = []
                for item in sorted(price_data, key=lambda x: x['timestamp']):
                    timestamp_key = item['timestamp'].isoformat()
                    if timestamp_key not in seen_timestamps:
                        seen_timestamps.add(timestamp_key)
                        unique_data.append(item)
                price_data = unique_data[-100:]  # Últimos 100 pontos
        
        # Obtém dados de sentimento recente
        sentiment_cutoff = datetime.utcnow() - timedelta(hours=6)
        recent_news = NewsData.query.filter(
            NewsData.created_at >= sentiment_cutoff
        ).all()
        
        # Calcula sentimento geral
        if recent_news:
            news_data = []
            for news in recent_news:
                news_data.append({
                    'sentiment_score': news.sentiment_score or 0.0,
                    'sentiment_label': news.sentiment_label or 'neutral',
                    'is_currency_related': True  # Assumimos relevância
                })
            sentiment_summary = sentiment_analyzer.calculate_overall_sentiment(news_data)
        else:
            sentiment_summary = {
                'overall_sentiment': 0.0,
                'total_news': 0,
                'currency_related_news': 0
            }
        
        # Gera sinal usando o algoritmo avançado
        signal = trading_algorithm.generate_trading_signal(
            price_data=price_data,
            sentiment_data=sentiment_summary,
            current_price=current_rate['price']
        )
        
        # Salva o sinal no banco
        trading_signal_record = TradingSignal(
            signal_type=signal.signal_type,
            confidence=signal.confidence,
            price_at_signal=signal.price_at_signal,
            reasoning=signal.reasoning
        )
        db.session.add(trading_signal_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'signal_type': signal.signal_type,
                'confidence': round(signal.confidence, 3),
                'current_price': signal.price_at_signal,
                'reasoning': signal.reasoning,
                'technical_score': round(signal.technical_score, 3),
                'sentiment_score': round(signal.sentiment_score, 3),
                'combined_score': round(signal.combined_score, 3),
                'timestamp': signal.timestamp.isoformat(),
                'data_points_used': len(price_data),
                'news_analyzed': sentiment_summary['total_news']
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar sinal de trading: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trading_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """Executa backtest da estratégia de trading"""
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 30)
        
        # Obtém dados históricos para backtest
        historical_data = data_collector.get_historical_data(days=days_back)
        
        if len(historical_data) < 20:
            return jsonify({
                'success': False,
                'error': f'Dados insuficientes para backtest. Encontrados {len(historical_data)} pontos, mínimo 20 necessários.'
            }), 400
        
        # Executa backtest
        backtest_results = trading_algorithm.backtest_strategy(
            historical_data=historical_data,
            historical_sentiment=[]  # Simplificado para esta versão
        )
        
        return jsonify({
            'success': True,
            'data': {
                'backtest_period_days': days_back,
                'data_points': len(historical_data),
                'results': backtest_results
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no backtest: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trading_bp.route('/optimize-parameters', methods=['POST'])
def optimize_algorithm_parameters():
    """Otimiza parâmetros do algoritmo baseado em dados históricos"""
    try:
        data = request.get_json() or {}
        days_back = data.get('days_back', 60)
        
        # Obtém dados históricos para otimização
        historical_data = data_collector.get_historical_data(days=days_back)
        
        if len(historical_data) < 50:
            return jsonify({
                'success': False,
                'error': f'Dados insuficientes para otimização. Encontrados {len(historical_data)} pontos, mínimo 50 necessários.'
            }), 400
        
        # Executa otimização
        optimization_results = trading_algorithm.optimize_parameters(historical_data)
        
        return jsonify({
            'success': True,
            'data': {
                'optimization_period_days': days_back,
                'data_points': len(historical_data),
                'results': optimization_results
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trading_bp.route('/technical-analysis', methods=['GET'])
def get_technical_analysis():
    """Obtém análise técnica detalhada dos dados atuais"""
    try:
        hours_back = request.args.get('hours_back', 48, type=int)
        
        # Obtém dados de preço recentes
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        price_query = CurrencyData.query.filter(
            CurrencyData.timestamp >= cutoff_time
        ).order_by(CurrencyData.timestamp.asc()).all()
        
        price_data = [
            {
                'price': record.price,
                'timestamp': record.timestamp,
                'source': record.source
            }
            for record in price_query
        ]
        
        # Se poucos dados, complementa com históricos
        if len(price_data) < 20:
            historical_data = data_collector.get_historical_data(days=7)
            if historical_data:
                price_data.extend(historical_data)
                price_data = sorted(price_data, key=lambda x: x['timestamp'])[-100:]
        
        if len(price_data) < 2:
            return jsonify({
                'success': False,
                'error': 'Dados insuficientes para análise técnica'
            }), 400
        
        # Calcula indicadores técnicos
        technical_indicators = trading_algorithm.calculate_technical_indicators(price_data)
        
        # Adiciona informações contextuais
        current_price = price_data[-1]['price']
        price_24h_ago = price_data[max(0, len(price_data)-24)]['price'] if len(price_data) >= 24 else price_data[0]['price']
        price_change_24h = (current_price - price_24h_ago) / price_24h_ago
        
        return jsonify({
            'success': True,
            'data': {
                'current_price': current_price,
                'price_change_24h': round(price_change_24h, 4),
                'data_points_analyzed': len(price_data),
                'analysis_period_hours': hours_back,
                'technical_indicators': {
                    'momentum': round(technical_indicators['momentum'], 4),
                    'volatility': round(technical_indicators['volatility'], 4),
                    'trend': round(technical_indicators['trend'], 4),
                    'rsi': round(technical_indicators['rsi'], 2),
                    'price_change': round(technical_indicators['price_change'], 4),
                    'technical_score': round(technical_indicators['technical_score'], 3)
                },
                'interpretation': {
                    'momentum': 'Positivo' if technical_indicators['momentum'] > 0.01 else 'Negativo' if technical_indicators['momentum'] < -0.01 else 'Neutro',
                    'trend': 'Alta' if technical_indicators['trend'] > 0.01 else 'Baixa' if technical_indicators['trend'] < -0.01 else 'Lateral',
                    'rsi_status': 'Sobrecompra' if technical_indicators['rsi'] > 70 else 'Sobrevenda' if technical_indicators['rsi'] < 30 else 'Normal',
                    'overall': 'Bullish' if technical_indicators['technical_score'] > 0.2 else 'Bearish' if technical_indicators['technical_score'] < -0.2 else 'Neutro'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na análise técnica: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trading_bp.route('/algorithm-status', methods=['GET'])
def get_algorithm_status():
    """Obtém status e configuração atual do algoritmo"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'algorithm_parameters': {
                    'sentiment_weight': trading_algorithm.sentiment_weight,
                    'technical_weight': trading_algorithm.technical_weight,
                    'buy_threshold': trading_algorithm.buy_threshold,
                    'sell_threshold': trading_algorithm.sell_threshold,
                    'volatility_window': trading_algorithm.volatility_window,
                    'momentum_window': trading_algorithm.momentum_window,
                    'trend_window': trading_algorithm.trend_window
                },
                'last_signals': [],  # Será preenchido com últimos sinais
                'algorithm_version': '1.0',
                'status': 'active'
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status do algoritmo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trading_bp.route('/update-parameters', methods=['POST'])
def update_algorithm_parameters():
    """Atualiza parâmetros do algoritmo"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados não fornecidos'
            }), 400
        
        # Atualiza parâmetros se fornecidos
        if 'sentiment_weight' in data:
            sentiment_weight = float(data['sentiment_weight'])
            if 0 <= sentiment_weight <= 1:
                trading_algorithm.sentiment_weight = sentiment_weight
                trading_algorithm.technical_weight = 1 - sentiment_weight
        
        if 'buy_threshold' in data:
            buy_threshold = float(data['buy_threshold'])
            if 0 <= buy_threshold <= 1:
                trading_algorithm.buy_threshold = buy_threshold
        
        if 'sell_threshold' in data:
            sell_threshold = float(data['sell_threshold'])
            if -1 <= sell_threshold <= 0:
                trading_algorithm.sell_threshold = sell_threshold
        
        return jsonify({
            'success': True,
            'message': 'Parâmetros atualizados com sucesso',
            'current_parameters': {
                'sentiment_weight': trading_algorithm.sentiment_weight,
                'technical_weight': trading_algorithm.technical_weight,
                'buy_threshold': trading_algorithm.buy_threshold,
                'sell_threshold': trading_algorithm.sell_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao atualizar parâmetros: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

