import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraperService:
    """Serviço para coleta de notícias financeiras de fontes gratuitas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_yahoo_finance_news(self, max_articles: int = 20) -> List[Dict]:
        """Coleta notícias do Yahoo Finance"""
        articles = []
        
        try:
            # URL das notícias financeiras do Yahoo Finance
            url = "https://finance.yahoo.com/news/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Erro ao acessar Yahoo Finance: {response.status_code}")
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca por artigos de notícias
            news_items = soup.find_all('h3', class_='clamp')[:max_articles]
            
            for item in news_items:
                try:
                    # Extrai o link e título
                    link_element = item.find('a')
                    if not link_element:
                        continue
                    
                    title = link_element.get_text(strip=True)
                    relative_url = link_element.get('href')
                    
                    if not relative_url:
                        continue
                    
                    # Constrói URL completa
                    full_url = urljoin("https://finance.yahoo.com", relative_url)
                    
                    # Tenta extrair o conteúdo do artigo
                    content = self._extract_article_content(full_url)
                    
                    article = {
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'yahoo_finance',
                        'published_at': datetime.now(),  # Yahoo não fornece data facilmente
                        'scraped_at': datetime.now()
                    }
                    
                    articles.append(article)
                    
                    # Delay para evitar sobrecarga
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar artigo do Yahoo Finance: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao coletar notícias do Yahoo Finance: {e}")
        
        logger.info(f"Coletados {len(articles)} artigos do Yahoo Finance")
        return articles
    
    def scrape_investing_news(self, max_articles: int = 20) -> List[Dict]:
        """Coleta notícias do Investing.com"""
        articles = []
        
        try:
            # URL das notícias de forex do Investing.com
            url = "https://br.investing.com/news/forex-news"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Erro ao acessar Investing.com: {response.status_code}")
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca por artigos de notícias
            news_items = soup.find_all('article', class_='articleItem')[:max_articles]
            
            for item in news_items:
                try:
                    # Extrai título
                    title_element = item.find('a', class_='title')
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    relative_url = title_element.get('href')
                    
                    if not relative_url:
                        continue
                    
                    # Constrói URL completa
                    full_url = urljoin("https://br.investing.com", relative_url)
                    
                    # Extrai data de publicação
                    date_element = item.find('time')
                    published_at = datetime.now()
                    if date_element:
                        try:
                            date_str = date_element.get('datetime')
                            if date_str:
                                published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Tenta extrair o conteúdo do artigo
                    content = self._extract_article_content(full_url)
                    
                    article = {
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'investing_com',
                        'published_at': published_at,
                        'scraped_at': datetime.now()
                    }
                    
                    articles.append(article)
                    
                    # Delay para evitar sobrecarga
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar artigo do Investing.com: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao coletar notícias do Investing.com: {e}")
        
        logger.info(f"Coletados {len(articles)} artigos do Investing.com")
        return articles
    
    def scrape_reuters_business(self, max_articles: int = 15) -> List[Dict]:
        """Coleta notícias de negócios da Reuters"""
        articles = []
        
        try:
            url = "https://www.reuters.com/business/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Erro ao acessar Reuters: {response.status_code}")
                return articles
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca por links de artigos
            article_links = soup.find_all('a', href=re.compile(r'/business/'))[:max_articles]
            
            for link in article_links:
                try:
                    title_element = link.find(['h3', 'h4', 'span'])
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    if len(title) < 10:  # Filtrar títulos muito curtos
                        continue
                    
                    relative_url = link.get('href')
                    if not relative_url:
                        continue
                    
                    full_url = urljoin("https://www.reuters.com", relative_url)
                    
                    # Tenta extrair o conteúdo do artigo
                    content = self._extract_article_content(full_url)
                    
                    article = {
                        'title': title,
                        'url': full_url,
                        'content': content,
                        'source': 'reuters',
                        'published_at': datetime.now(),
                        'scraped_at': datetime.now()
                    }
                    
                    articles.append(article)
                    
                    # Delay para evitar sobrecarga
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar artigo da Reuters: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao coletar notícias da Reuters: {e}")
        
        logger.info(f"Coletados {len(articles)} artigos da Reuters")
        return articles
    
    def _extract_article_content(self, url: str) -> str:
        """Extrai o conteúdo de um artigo específico"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return ""
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Tenta diferentes seletores comuns para conteúdo de artigos
            content_selectors = [
                'div[data-module="ArticleBody"]',
                'div.caas-body',
                'div.article-body',
                'div.story-body',
                'div.content',
                'article',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    break
            
            # Se não encontrou com seletores específicos, pega todos os parágrafos
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Limita o tamanho do conteúdo
            return content[:2000] if content else ""
            
        except Exception as e:
            logger.warning(f"Erro ao extrair conteúdo de {url}: {e}")
            return ""
    
    def collect_all_news(self, max_per_source: int = 15) -> List[Dict]:
        """Coleta notícias de todas as fontes disponíveis"""
        all_articles = []
        
        # Coleta de diferentes fontes
        sources = [
            ('yahoo_finance', self.scrape_yahoo_finance_news),
            ('investing_com', self.scrape_investing_news),
            ('reuters', self.scrape_reuters_business)
        ]
        
        for source_name, scraper_func in sources:
            try:
                logger.info(f"Coletando notícias de {source_name}...")
                articles = scraper_func(max_per_source)
                all_articles.extend(articles)
                
                # Delay entre fontes
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Erro ao coletar de {source_name}: {e}")
                continue
        
        # Remove duplicatas baseado no título
        seen_titles = set()
        unique_articles = []
        
        for article in all_articles:
            title_lower = article['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        logger.info(f"Total de artigos únicos coletados: {len(unique_articles)}")
        return unique_articles

# Instância global do scraper
news_scraper = NewsScraperService()

