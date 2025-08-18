from textblob import TextBlob
import re
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analisador de sentimento para notícias financeiras"""
    
    def __init__(self):
        # Palavras-chave específicas do mercado financeiro
        self.positive_keywords = {
            'alta', 'subir', 'crescimento', 'lucro', 'ganho', 'valorização', 'otimismo',
            'bull', 'bullish', 'rally', 'gain', 'profit', 'growth', 'rise', 'increase',
            'positive', 'strong', 'robust', 'recovery', 'boom', 'surge', 'soar',
            'upgrade', 'outperform', 'buy', 'compra', 'recomendação de compra'
        }
        
        self.negative_keywords = {
            'queda', 'baixa', 'perda', 'prejuízo', 'desvalorização', 'pessimismo',
            'bear', 'bearish', 'crash', 'loss', 'decline', 'fall', 'drop', 'decrease',
            'negative', 'weak', 'recession', 'crisis', 'plunge', 'tumble', 'slump',
            'downgrade', 'underperform', 'sell', 'venda', 'recomendação de venda'
        }
        
        # Palavras relacionadas ao dólar e câmbio
        self.currency_keywords = {
            'dólar', 'dollar', 'usd', 'real', 'brl', 'câmbio', 'exchange', 'forex',
            'moeda', 'currency', 'taxa de câmbio', 'exchange rate', 'mini dólar',
            'futuro', 'futures', 'b3', 'bovespa'
        }
    
    def clean_text(self, text: str) -> str:
        """Limpa e prepara o texto para análise"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove caracteres especiais excessivos
        text = re.sub(r'[^\w\s\.\,\!\?\-]', ' ', text)
        
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def calculate_keyword_sentiment(self, text: str) -> float:
        """Calcula sentimento baseado em palavras-chave específicas do mercado financeiro"""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            return 0.0
        
        # Calcula score normalizado entre -1 e 1
        sentiment_score = (positive_count - negative_count) / total_keywords
        return sentiment_score
    
    def is_currency_related(self, text: str) -> bool:
        """Verifica se o texto está relacionado a câmbio/dólar"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.currency_keywords)
    
    def analyze_sentiment(self, text: str, title: str = "") -> Dict:
        """Analisa o sentimento de um texto usando múltiplas abordagens"""
        
        # Combina título e conteúdo para análise
        full_text = f"{title} {text}".strip()
        cleaned_text = self.clean_text(full_text)
        
        if not cleaned_text:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'is_currency_related': False,
                'method': 'empty_text'
            }
        
        # Verifica se é relacionado a câmbio
        is_currency_related = self.is_currency_related(cleaned_text)
        
        # Análise com TextBlob
        try:
            blob = TextBlob(cleaned_text)
            textblob_sentiment = blob.sentiment.polarity
            textblob_confidence = abs(blob.sentiment.polarity)
        except Exception as e:
            logger.warning(f"Erro na análise TextBlob: {e}")
            textblob_sentiment = 0.0
            textblob_confidence = 0.0
        
        # Análise com palavras-chave específicas
        keyword_sentiment = self.calculate_keyword_sentiment(cleaned_text)
        
        # Combina os métodos (dá mais peso para palavras-chave se for relacionado a câmbio)
        if is_currency_related and abs(keyword_sentiment) > 0.1:
            # Para textos relacionados a câmbio, dá mais peso às palavras-chave
            final_sentiment = (keyword_sentiment * 0.7) + (textblob_sentiment * 0.3)
            confidence = min(abs(keyword_sentiment) + 0.2, 1.0)
            method = 'keyword_weighted'
        else:
            # Para outros textos, usa principalmente TextBlob
            final_sentiment = (textblob_sentiment * 0.7) + (keyword_sentiment * 0.3)
            confidence = textblob_confidence
            method = 'textblob_weighted'
        
        # Determina o rótulo do sentimento
        if final_sentiment > 0.1:
            sentiment_label = 'positive'
        elif final_sentiment < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'sentiment_score': round(final_sentiment, 3),
            'sentiment_label': sentiment_label,
            'confidence': round(confidence, 3),
            'is_currency_related': is_currency_related,
            'method': method,
            'textblob_score': round(textblob_sentiment, 3),
            'keyword_score': round(keyword_sentiment, 3)
        }
    
    def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """Analisa sentimento de uma lista de notícias"""
        analyzed_news = []
        
        for news in news_list:
            try:
                title = news.get('title', '')
                content = news.get('content', '')
                
                sentiment_result = self.analyze_sentiment(content, title)
                
                # Adiciona os resultados da análise ao objeto de notícia
                news_with_sentiment = news.copy()
                news_with_sentiment.update({
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_label': sentiment_result['sentiment_label'],
                    'sentiment_confidence': sentiment_result['confidence'],
                    'is_currency_related': sentiment_result['is_currency_related'],
                    'sentiment_method': sentiment_result['method']
                })
                
                analyzed_news.append(news_with_sentiment)
                
            except Exception as e:
                logger.warning(f"Erro ao analisar sentimento da notícia: {e}")
                # Adiciona valores padrão em caso de erro
                news_with_sentiment = news.copy()
                news_with_sentiment.update({
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'sentiment_confidence': 0.0,
                    'is_currency_related': False,
                    'sentiment_method': 'error'
                })
                analyzed_news.append(news_with_sentiment)
        
        return analyzed_news
    
    def calculate_overall_sentiment(self, news_list: List[Dict]) -> Dict:
        """Calcula o sentimento geral de uma lista de notícias"""
        
        if not news_list:
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'total_news': 0,
                'currency_related_news': 0,
                'positive_news': 0,
                'negative_news': 0,
                'neutral_news': 0
            }
        
        # Filtra notícias relacionadas a câmbio para dar mais peso
        currency_news = [news for news in news_list if news.get('is_currency_related', False)]
        
        # Calcula sentimento médio
        if currency_news:
            # Se há notícias relacionadas a câmbio, usa apenas essas
            relevant_news = currency_news
            weight_factor = 1.5  # Dá mais peso para notícias de câmbio
        else:
            # Caso contrário, usa todas as notícias
            relevant_news = news_list
            weight_factor = 1.0
        
        sentiment_scores = [news.get('sentiment_score', 0.0) for news in relevant_news]
        
        if sentiment_scores:
            overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) * weight_factor
            overall_sentiment = max(-1.0, min(1.0, overall_sentiment))  # Limita entre -1 e 1
        else:
            overall_sentiment = 0.0
        
        # Conta tipos de sentimento
        positive_count = sum(1 for news in news_list if news.get('sentiment_label') == 'positive')
        negative_count = sum(1 for news in news_list if news.get('sentiment_label') == 'negative')
        neutral_count = len(news_list) - positive_count - negative_count
        
        # Determina rótulo geral
        if overall_sentiment > 0.1:
            sentiment_label = 'positive'
        elif overall_sentiment < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'overall_sentiment': round(overall_sentiment, 3),
            'sentiment_label': sentiment_label,
            'total_news': len(news_list),
            'currency_related_news': len(currency_news),
            'positive_news': positive_count,
            'negative_news': negative_count,
            'neutral_news': neutral_count
        }

# Instância global do analisador
sentiment_analyzer = SentimentAnalyzer()

