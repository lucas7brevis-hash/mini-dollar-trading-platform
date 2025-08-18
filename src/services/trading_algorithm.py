import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Estrutura para sinal de trading"""
    signal_type: str  # BUY, SELL, HOLD
    confidence: float  # 0 to 1
    price_at_signal: float
    reasoning: str
    timestamp: datetime
    technical_score: float
    sentiment_score: float
    combined_score: float

class TradingAlgorithm:
    """Algoritmo avançado de decisão de compra/venda para mini dólar"""
    
    def __init__(self):
        # Parâmetros do algoritmo
        self.sentiment_weight = 0.4
        self.technical_weight = 0.6
        
        # Thresholds para sinais
        self.buy_threshold = 0.3
        self.sell_threshold = -0.3
        
        # Parâmetros técnicos
        self.volatility_window = 20
        self.momentum_window = 10
        self.trend_window = 50
        
    def calculate_technical_indicators(self, price_data: List[Dict]) -> Dict:
        """Calcula indicadores técnicos baseados nos dados de preço"""
        
        if len(price_data) < 2:
            return {
                'momentum': 0.0,
                'volatility': 0.0,
                'trend': 0.0,
                'rsi': 50.0,
                'price_change': 0.0,
                'technical_score': 0.0
            }
        
        # Converte para DataFrame
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['price'] = df['price'].astype(float)
        
        # Calcula indicadores
        indicators = {}
        
        # 1. Momentum (taxa de mudança de preço)
        if len(df) >= self.momentum_window:
            momentum_window = min(self.momentum_window, len(df))
            current_price = df['price'].iloc[-1]
            past_price = df['price'].iloc[-momentum_window]
            indicators['momentum'] = (current_price - past_price) / past_price
        else:
            indicators['momentum'] = 0.0
        
        # 2. Volatilidade (desvio padrão dos retornos)
        if len(df) >= 2:
            df['returns'] = df['price'].pct_change()
            volatility_window = min(self.volatility_window, len(df))
            recent_returns = df['returns'].tail(volatility_window)
            indicators['volatility'] = recent_returns.std()
        else:
            indicators['volatility'] = 0.0
        
        # 3. Tendência (média móvel simples)
        if len(df) >= self.trend_window:
            trend_window = min(self.trend_window, len(df))
            sma = df['price'].tail(trend_window).mean()
            current_price = df['price'].iloc[-1]
            indicators['trend'] = (current_price - sma) / sma
        else:
            indicators['trend'] = 0.0
        
        # 4. RSI simplificado
        if len(df) >= 14:
            delta = df['price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
        else:
            indicators['rsi'] = 50.0
        
        # 5. Mudança de preço recente
        if len(df) >= 2:
            current_price = df['price'].iloc[-1]
            previous_price = df['price'].iloc[-2]
            indicators['price_change'] = (current_price - previous_price) / previous_price
        else:
            indicators['price_change'] = 0.0
        
        # Calcula score técnico combinado
        technical_score = self._calculate_technical_score(indicators)
        indicators['technical_score'] = technical_score
        
        return indicators
    
    def _calculate_technical_score(self, indicators: Dict) -> float:
        """Calcula score técnico combinado (-1 a 1)"""
        
        # Normaliza RSI para -1 a 1 (50 = 0, 0 = -1, 100 = 1)
        rsi_normalized = (indicators['rsi'] - 50) / 50
        
        # Normaliza momentum (limita entre -0.1 e 0.1 para evitar valores extremos)
        momentum_normalized = np.clip(indicators['momentum'] * 10, -1, 1)
        
        # Normaliza tendência (limita entre -0.05 e 0.05)
        trend_normalized = np.clip(indicators['trend'] * 20, -1, 1)
        
        # Volatilidade como fator de risco (alta volatilidade reduz confiança)
        volatility_factor = 1 - min(indicators['volatility'] * 100, 0.5)
        
        # Combina indicadores com pesos
        technical_score = (
            momentum_normalized * 0.4 +
            trend_normalized * 0.3 +
            rsi_normalized * 0.2 +
            indicators['price_change'] * 100 * 0.1
        ) * volatility_factor
        
        return np.clip(technical_score, -1, 1)
    
    def analyze_sentiment_impact(self, sentiment_data: Dict) -> float:
        """Analisa o impacto do sentimento no mercado"""
        
        overall_sentiment = sentiment_data.get('overall_sentiment', 0.0)
        currency_related_news = sentiment_data.get('currency_related_news', 0)
        total_news = sentiment_data.get('total_news', 0)
        
        # Ajusta o peso do sentimento baseado na quantidade de notícias relacionadas
        if total_news > 0:
            relevance_factor = min(currency_related_news / total_news, 1.0)
        else:
            relevance_factor = 0.0
        
        # Aplica fator de relevância ao sentimento
        adjusted_sentiment = overall_sentiment * (0.5 + 0.5 * relevance_factor)
        
        # Aplica fator de confiança baseado na quantidade de notícias
        confidence_factor = min(total_news / 10, 1.0)  # Máximo de confiança com 10+ notícias
        
        final_sentiment_score = adjusted_sentiment * confidence_factor
        
        return np.clip(final_sentiment_score, -1, 1)
    
    def generate_trading_signal(self, 
                              price_data: List[Dict], 
                              sentiment_data: Dict,
                              current_price: float) -> TradingSignal:
        """Gera sinal de trading baseado em análise técnica e sentimento"""
        
        # Calcula indicadores técnicos
        technical_indicators = self.calculate_technical_indicators(price_data)
        technical_score = technical_indicators['technical_score']
        
        # Analisa sentimento
        sentiment_score = self.analyze_sentiment_impact(sentiment_data)
        
        # Combina scores técnico e de sentimento
        combined_score = (
            technical_score * self.technical_weight +
            sentiment_score * self.sentiment_weight
        )
        
        # Determina tipo de sinal
        if combined_score >= self.buy_threshold:
            signal_type = "BUY"
            confidence = min(0.6 + abs(combined_score) * 0.4, 1.0)
        elif combined_score <= self.sell_threshold:
            signal_type = "SELL"
            confidence = min(0.6 + abs(combined_score) * 0.4, 1.0)
        else:
            signal_type = "HOLD"
            confidence = 0.5 + abs(combined_score) * 0.2
        
        # Gera reasoning detalhado
        reasoning = self._generate_reasoning(
            signal_type, technical_indicators, sentiment_data, 
            technical_score, sentiment_score, combined_score
        )
        
        return TradingSignal(
            signal_type=signal_type,
            confidence=confidence,
            price_at_signal=current_price,
            reasoning=reasoning,
            timestamp=datetime.now(),
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            combined_score=combined_score
        )
    
    def _generate_reasoning(self, signal_type: str, technical_indicators: Dict, 
                          sentiment_data: Dict, technical_score: float,
                          sentiment_score: float, combined_score: float) -> str:
        """Gera explicação detalhada do sinal"""
        
        reasoning_parts = []
        
        # Análise técnica
        if abs(technical_score) > 0.2:
            direction = "alta" if technical_score > 0 else "baixa"
            reasoning_parts.append(
                f"Análise técnica indica tendência de {direction} "
                f"(score: {technical_score:.3f})"
            )
            
            # Detalhes dos indicadores
            if technical_indicators['momentum'] > 0.02:
                reasoning_parts.append("Momentum positivo detectado")
            elif technical_indicators['momentum'] < -0.02:
                reasoning_parts.append("Momentum negativo detectado")
            
            if technical_indicators['rsi'] > 70:
                reasoning_parts.append("RSI indica sobrecompra")
            elif technical_indicators['rsi'] < 30:
                reasoning_parts.append("RSI indica sobrevenda")
        
        # Análise de sentimento
        if abs(sentiment_score) > 0.1:
            sentiment_direction = "positivo" if sentiment_score > 0 else "negativo"
            reasoning_parts.append(
                f"Sentimento das notícias é {sentiment_direction} "
                f"(score: {sentiment_score:.3f})"
            )
            
            total_news = sentiment_data.get('total_news', 0)
            currency_news = sentiment_data.get('currency_related_news', 0)
            
            if total_news > 0:
                reasoning_parts.append(
                    f"Baseado em {total_news} notícias "
                    f"({currency_news} relacionadas ao câmbio)"
                )
        
        # Sinal final
        if signal_type == "BUY":
            reasoning_parts.append(
                f"Recomendação de COMPRA com score combinado de {combined_score:.3f}"
            )
        elif signal_type == "SELL":
            reasoning_parts.append(
                f"Recomendação de VENDA com score combinado de {combined_score:.3f}"
            )
        else:
            reasoning_parts.append(
                f"Recomendação de MANTER posição com score neutro de {combined_score:.3f}"
            )
        
        return ". ".join(reasoning_parts) + "."
    
    def backtest_strategy(self, historical_data: List[Dict], 
                         historical_sentiment: List[Dict]) -> Dict:
        """Realiza backtest da estratégia"""
        
        if len(historical_data) < 10:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        # Simula trades baseados nos sinais históricos
        trades = []
        position = None  # None, 'LONG', 'SHORT'
        entry_price = 0.0
        
        for i in range(10, len(historical_data)):
            # Dados para análise (últimos 10 pontos)
            price_window = historical_data[max(0, i-50):i]
            current_price = historical_data[i]['price']
            
            # Sentimento (simplificado para backtest)
            sentiment_data = {
                'overall_sentiment': 0.0,
                'total_news': 5,
                'currency_related_news': 3
            }
            
            # Gera sinal
            signal = self.generate_trading_signal(
                price_window, sentiment_data, current_price
            )
            
            # Executa trades baseados no sinal
            if signal.signal_type == "BUY" and position != 'LONG':
                if position == 'SHORT':
                    # Fecha posição short
                    profit = entry_price - current_price
                    trades.append({
                        'type': 'SHORT',
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'profit': profit,
                        'return': profit / entry_price
                    })
                
                # Abre posição long
                position = 'LONG'
                entry_price = current_price
                
            elif signal.signal_type == "SELL" and position != 'SHORT':
                if position == 'LONG':
                    # Fecha posição long
                    profit = current_price - entry_price
                    trades.append({
                        'type': 'LONG',
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'profit': profit,
                        'return': profit / entry_price
                    })
                
                # Abre posição short
                position = 'SHORT'
                entry_price = current_price
        
        # Calcula métricas de performance
        if not trades:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        profitable_trades = sum(1 for trade in trades if trade['profit'] > 0)
        total_return = sum(trade['return'] for trade in trades)
        returns = [trade['return'] for trade in trades]
        
        # Calcula drawdown máximo
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = running_max - cumulative_returns
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
        
        # Calcula Sharpe ratio (simplificado)
        if len(returns) > 1:
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        return {
            'total_trades': len(trades),
            'profitable_trades': profitable_trades,
            'win_rate': profitable_trades / len(trades),
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'average_return_per_trade': total_return / len(trades)
        }
    
    def optimize_parameters(self, historical_data: List[Dict]) -> Dict:
        """Otimiza parâmetros do algoritmo baseado em dados históricos"""
        
        best_params = {
            'sentiment_weight': self.sentiment_weight,
            'technical_weight': self.technical_weight,
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold
        }
        
        best_performance = -float('inf')
        
        # Grid search simples
        sentiment_weights = [0.2, 0.3, 0.4, 0.5, 0.6]
        thresholds = [0.2, 0.25, 0.3, 0.35, 0.4]
        
        for sentiment_weight in sentiment_weights:
            for threshold in thresholds:
                # Atualiza parâmetros temporariamente
                original_params = (
                    self.sentiment_weight, self.technical_weight,
                    self.buy_threshold, self.sell_threshold
                )
                
                self.sentiment_weight = sentiment_weight
                self.technical_weight = 1 - sentiment_weight
                self.buy_threshold = threshold
                self.sell_threshold = -threshold
                
                # Testa performance
                backtest_result = self.backtest_strategy(historical_data, [])
                
                # Métrica de performance combinada
                performance_score = (
                    backtest_result['total_return'] * 0.4 +
                    backtest_result['win_rate'] * 0.3 +
                    backtest_result['sharpe_ratio'] * 0.2 -
                    backtest_result['max_drawdown'] * 0.1
                )
                
                if performance_score > best_performance:
                    best_performance = performance_score
                    best_params = {
                        'sentiment_weight': sentiment_weight,
                        'technical_weight': 1 - sentiment_weight,
                        'buy_threshold': threshold,
                        'sell_threshold': -threshold
                    }
                
                # Restaura parâmetros originais
                (self.sentiment_weight, self.technical_weight,
                 self.buy_threshold, self.sell_threshold) = original_params
        
        return {
            'best_params': best_params,
            'best_performance': best_performance,
            'optimization_completed': True
        }

# Instância global do algoritmo
trading_algorithm = TradingAlgorithm()

