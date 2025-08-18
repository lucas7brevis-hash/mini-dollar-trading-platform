from flask import Blueprint, jsonify, request
from src.services.data_collector import data_collector
from src.services.news_scraper import news_scraper
from src.services.sentiment_analyzer import sentiment_analyzer
from src.models.user import db
from src.models.financial_data import CurrencyData, NewsData, TradingSignal
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/current-rate', methods=['GET'])
def get_current_rate():
    """Obtém a cotação atual do USD/BRL"""
    try:
        rate_data = data_collector.get_current_rate()
        
        if rate_data:
            # Salva no banco de dados
            currency_data = CurrencyData(
                symbol=rate_data['symbol'],
                price=rate_data['price'],
                timestamp=rate_data['timestamp'],
                source=rate_data['source']
            )
            db.session.add(currency_data)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': rate_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter a cotação atual'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro ao obter cotação atual: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/historical-rates', methods=['GET'])
def get_historical_rates():
    """Obtém dados históricos do USD/BRL"""
    try:
        days = request.args.get('days', 30, type=int)
        days = min(days, 365)  # Limita a 1 ano
        
        historical_data = data_collector.get_historical_data(days)
        
        return jsonify({
            'success': True,
            'data': historical_data,
            'count': len(historical_data)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter dados históricos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/collect-news', methods=['POST'])
def collect_news():
    """Coleta notícias financeiras e analisa sentimento"""
    try:
        max_per_source = request.json.get('max_per_source', 15) if request.json else 15
        
        # Coleta notícias
        logger.info("Iniciando coleta de notícias...")
        news_articles = news_scraper.collect_all_news(max_per_source)
        
        if not news_articles:
            return jsonify({
                'success': False,
                'error': 'Nenhuma notícia foi coletada'
            }), 404
        
        # Analisa sentimento
        logger.info("Analisando sentimento das notícias...")
        analyzed_news = sentiment_analyzer.analyze_news_batch(news_articles)
        
        # Salva no banco de dados
        saved_count = 0
        for news in analyzed_news:
            try:
                news_data = NewsData(
                    title=news['title'],
                    content=news.get('content', ''),
                    url=news.get('url', ''),
                    source=news['source'],
                    published_at=news['published_at'],
                    sentiment_score=news.get('sentiment_score', 0.0),
                    sentiment_label=news.get('sentiment_label', 'neutral')
                )
                db.session.add(news_data)
                saved_count += 1
            except Exception as e:
                logger.warning(f"Erro ao salvar notícia: {e}")
                continue
        
        db.session.commit()
        
        # Calcula sentimento geral
        overall_sentiment = sentiment_analyzer.calculate_overall_sentiment(analyzed_news)
        
        return jsonify({
            'success': True,
            'data': {
                'total_collected': len(news_articles),
                'total_saved': saved_count,
                'overall_sentiment': overall_sentiment,
                'news_sample': analyzed_news[:5]  # Retorna apenas uma amostra
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao coletar notícias: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/news', methods=['GET'])
def get_news():
    """Obtém notícias salvas no banco de dados"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)  # Limita a 200 notícias
        
        # Busca notícias mais recentes
        news_query = NewsData.query.order_by(NewsData.created_at.desc()).limit(limit)
        news_list = [news.to_dict() for news in news_query.all()]
        
        return jsonify({
            'success': True,
            'data': news_list,
            'count': len(news_list)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar notícias: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/sentiment-summary', methods=['GET'])
def get_sentiment_summary():
    """Obtém resumo do sentimento das notícias recentes"""
    try:
        hours = request.args.get('hours', 24, type=int)
        hours = min(hours, 168)  # Limita a 1 semana
        
        # Busca notícias das últimas X horas
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_news = NewsData.query.filter(NewsData.created_at >= cutoff_time).all()
        
        if not recent_news:
            return jsonify({
                'success': True,
                'data': {
                    'overall_sentiment': 0.0,
                    'sentiment_label': 'neutral',
                    'total_news': 0,
                    'currency_related_news': 0,
                    'positive_news': 0,
                    'negative_news': 0,
                    'neutral_news': 0
                }
            })
        
        # Converte para formato esperado pelo analisador
        news_data = []
        for news in recent_news:
            news_data.append({
                'sentiment_score': news.sentiment_score,
                'sentiment_label': news.sentiment_label,
                'is_currency_related': True  # Assumimos que todas são relevantes
            })
        
        # Calcula sentimento geral
        overall_sentiment = sentiment_analyzer.calculate_overall_sentiment(news_data)
        
        return jsonify({
            'success': True,
            'data': overall_sentiment
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular resumo de sentimento: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/trading-signal', methods=['GET'])
def get_trading_signal():
    """Gera sinal de trading baseado nos dados atuais"""
    try:
        # Obtém cotação atual
        current_rate = data_collector.get_current_rate()
        if not current_rate:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter cotação atual'
            }), 500
        
        # Obtém sentimento recente
        cutoff_time = datetime.utcnow() - timedelta(hours=6)
        recent_news = NewsData.query.filter(NewsData.created_at >= cutoff_time).all()
        
        # Calcula sentimento médio
        if recent_news:
            sentiment_scores = [news.sentiment_score for news in recent_news if news.sentiment_score is not None]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        else:
            avg_sentiment = 0.0
        
        # Lógica simples de sinal de trading
        signal_type = "HOLD"
        confidence = 0.5
        reasoning = "Sinal neutro baseado em dados limitados"
        
        if avg_sentiment > 0.2:
            signal_type = "BUY"
            confidence = min(0.7 + abs(avg_sentiment) * 0.3, 1.0)
            reasoning = f"Sentimento positivo das notícias ({avg_sentiment:.3f}) sugere tendência de alta do dólar"
        elif avg_sentiment < -0.2:
            signal_type = "SELL"
            confidence = min(0.7 + abs(avg_sentiment) * 0.3, 1.0)
            reasoning = f"Sentimento negativo das notícias ({avg_sentiment:.3f}) sugere tendência de baixa do dólar"
        
        # Salva o sinal no banco
        trading_signal = TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            price_at_signal=current_rate['price'],
            reasoning=reasoning
        )
        db.session.add(trading_signal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'signal_type': signal_type,
                'confidence': round(confidence, 3),
                'current_price': current_rate['price'],
                'reasoning': reasoning,
                'sentiment_score': round(avg_sentiment, 3),
                'news_count': len(recent_news),
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar sinal de trading: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/signals-history', methods=['GET'])
def get_signals_history():
    """Obtém histórico de sinais de trading"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 200)
        
        signals = TradingSignal.query.order_by(TradingSignal.timestamp.desc()).limit(limit).all()
        signals_data = [signal.to_dict() for signal in signals]
        
        return jsonify({
            'success': True,
            'data': signals_data,
            'count': len(signals_data)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de sinais: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@financial_bp.route('/set-alpha-vantage-key', methods=['POST'])
def set_alpha_vantage_key():
    """Define a chave da API Alpha Vantage"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Chave da API é obrigatória'
            }), 400
        
        data_collector.set_alpha_vantage_key(api_key)
        
        return jsonify({
            'success': True,
            'message': 'Chave Alpha Vantage configurada com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao configurar chave Alpha Vantage: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

