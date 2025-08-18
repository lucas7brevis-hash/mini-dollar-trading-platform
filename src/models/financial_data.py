from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CurrencyData(db.Model):
    __tablename__ = 'currency_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)  # USD/BRL
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=False)  # API source
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

class NewsData(db.Model):
    __tablename__ = 'news_data'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    url = db.Column(db.String(500))
    source = db.Column(db.String(100), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False)
    sentiment_score = db.Column(db.Float)  # -1 to 1
    sentiment_label = db.Column(db.String(20))  # positive, negative, neutral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_at': self.published_at.isoformat(),
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'created_at': self.created_at.isoformat()
        }

class TradingSignal(db.Model):
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_type = db.Column(db.String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)  # 0 to 1
    price_at_signal = db.Column(db.Float, nullable=False)
    reasoning = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'price_at_signal': self.price_at_signal,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat()
        }

