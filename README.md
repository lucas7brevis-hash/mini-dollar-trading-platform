# Mini Dólar Trading Platform

Uma plataforma inteligente em Python para análise em tempo real do cenário do dólar, fornecendo sinais de compra/venda para operações de mini dólar na B3.

## 🚀 Características Principais

### 📊 Análise Financeira Avançada
- **Cotação em tempo real** do USD/BRL via múltiplas fontes gratuitas
- **Indicadores técnicos** (RSI, Momentum, Tendência, Volatilidade)
- **Algoritmo de trading** com análise técnica e sentimento combinados
- **Backtesting** para validação de estratégias
- **Otimização automática** de parâmetros

### 📰 Análise de Sentimento
- **Coleta automática** de notícias financeiras (Yahoo Finance, Investing.com, Reuters)
- **Análise de sentimento** usando TextBlob + palavras-chave financeiras
- **Impacto no mercado** baseado em relevância das notícias
- **Score combinado** técnico + sentimento para decisões

### 🎯 Sinais de Trading
- **BUY/SELL/HOLD** com níveis de confiança
- **Explicações detalhadas** para cada sinal gerado
- **Histórico de sinais** para acompanhamento
- **Reasoning inteligente** baseado em múltiplos fatores

### 🌐 Interface Web Moderna
- **Design responsivo** com gradientes e animações
- **Atualização em tempo real** (30 segundos)
- **Dashboard interativo** com cards e indicadores
- **Ferramentas avançadas** (backtest, otimização, status)

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **yfinance** - Dados financeiros
- **TextBlob** - Análise de sentimento
- **BeautifulSoup** - Web scraping
- **pandas/numpy** - Análise de dados

### Frontend
- **HTML5/CSS3** - Interface moderna
- **JavaScript** - Interatividade
- **Font Awesome** - Ícones
- **Chart.js** - Gráficos (preparado)

### APIs Gratuitas Integradas
- **yfinance** - Cotações históricas e atuais
- **Alpha Vantage** - Dados financeiros (backup)
- **Twelve Data** - Forex (backup)
- **Yahoo Finance** - Notícias financeiras
- **Investing.com** - Notícias de mercado
- **Reuters** - Notícias globais

## 📁 Estrutura do Projeto

```
mini_dollar_platform/
├── src/
│   ├── main.py                 # Aplicação principal Flask
│   ├── models/
│   │   ├── user.py            # Modelo de usuário
│   │   └── financial_data.py  # Modelos financeiros
│   ├── routes/
│   │   ├── user.py            # Rotas de usuário
│   │   ├── financial_data.py  # Rotas de dados financeiros
│   │   └── trading.py         # Rotas de trading
│   ├── services/
│   │   ├── data_collector.py  # Coleta de dados financeiros
│   │   ├── news_scraper.py    # Coleta de notícias
│   │   ├── sentiment_analyzer.py # Análise de sentimento
│   │   └── trading_algorithm.py  # Algoritmo de trading
│   ├── static/
│   │   └── index.html         # Interface web
│   └── database/
│       └── app.db             # Banco SQLite
├── venv/                      # Ambiente virtual
├── init_db.py                 # Script de inicialização do DB
├── fix_db.py                  # Script de correção do DB
└── README.md                  # Esta documentação
```

## 🚀 Como Executar

### 1. Preparação do Ambiente
```bash
cd mini_dollar_platform
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados
```bash
python init_db.py
```

### 3. Executar a Aplicação
```bash
python src/main.py
```

### 4. Acessar a Interface
Abra o navegador em: `http://localhost:5000`

## 📊 APIs Disponíveis

### Dados Financeiros
- `GET /api/financial/current-rate` - Cotação atual USD/BRL
- `GET /api/financial/historical-rates` - Dados históricos
- `POST /api/financial/collect-news` - Coleta e analisa notícias
- `GET /api/financial/news` - Lista notícias salvas
- `GET /api/financial/sentiment-summary` - Resumo do sentimento
- `GET /api/financial/signals-history` - Histórico de sinais

### Trading e Análise
- `POST /api/trading/generate-signal` - Gera sinal de trading avançado
- `POST /api/trading/backtest` - Executa backtest da estratégia
- `POST /api/trading/optimize-parameters` - Otimiza parâmetros
- `GET /api/trading/technical-analysis` - Análise técnica detalhada
- `GET /api/trading/algorithm-status` - Status do algoritmo
- `POST /api/trading/update-parameters` - Atualiza parâmetros

## 🎯 Funcionalidades da Interface

### Dashboard Principal
- **Cotação USD/BRL** em tempo real com fonte e timestamp
- **Sinal de Trading** com tipo (BUY/SELL/HOLD) e confiança
- **Análise Técnica** com indicadores RSI, Momentum, Tendência, Volatilidade
- **Sentimento das Notícias** com emoji e score
- **Últimos Sinais** para acompanhamento histórico

### Ferramentas Avançadas
- **Backtest** - Testa estratégia em dados históricos
- **Otimização** - Encontra melhores parâmetros automaticamente
- **Status do Algoritmo** - Visualiza configuração atual

## 🧠 Algoritmo de Trading

### Indicadores Técnicos (60% do peso)
- **RSI** - Índice de Força Relativa
- **Momentum** - Taxa de mudança de preço
- **Tendência** - Média móvel simples
- **Volatilidade** - Desvio padrão dos retornos
- **Mudança de Preço** - Variação recente

### Análise de Sentimento (40% do peso)
- **Score de Sentimento** das notícias (-1 a +1)
- **Fator de Relevância** baseado em notícias relacionadas ao câmbio
- **Fator de Confiança** baseado na quantidade de notícias

### Sinais Gerados
- **BUY** - Score combinado ≥ 0.3
- **SELL** - Score combinado ≤ -0.3
- **HOLD** - Score entre -0.3 e 0.3

## 📈 Métricas de Performance

### Backtest
- **Total de Trades** executados
- **Taxa de Acerto** (win rate)
- **Retorno Total** da estratégia
- **Sharpe Ratio** (retorno ajustado ao risco)
- **Drawdown Máximo** (maior perda)

### Otimização
- **Grid Search** para encontrar melhores parâmetros
- **Performance Score** combinada
- **Validação cruzada** em dados históricos

## 🔧 Configurações

### Parâmetros do Algoritmo
- `sentiment_weight`: Peso da análise de sentimento (padrão: 0.4)
- `technical_weight`: Peso da análise técnica (padrão: 0.6)
- `buy_threshold`: Limite para sinal de compra (padrão: 0.3)
- `sell_threshold`: Limite para sinal de venda (padrão: -0.3)
- `volatility_window`: Janela para cálculo de volatilidade (padrão: 20)
- `momentum_window`: Janela para cálculo de momentum (padrão: 10)
- `trend_window`: Janela para cálculo de tendência (padrão: 50)

### Fontes de Dados
- **Primária**: yfinance (gratuita, sem limite)
- **Backup**: Alpha Vantage (500 calls/dia)
- **Backup**: Twelve Data (800 calls/dia)
- **Notícias**: Yahoo Finance, Investing.com, Reuters

## 🚨 Limitações e Considerações

### Dados Gratuitos
- **yfinance**: Pode ter atrasos de 15-20 minutos
- **APIs gratuitas**: Limites diários de requisições
- **Notícias**: Dependem de scraping (pode quebrar com mudanças nos sites)

### Uso Responsável
- **Não é aconselhamento financeiro** - Use por sua conta e risco
- **Backtesting não garante** performance futura
- **Sempre faça sua própria análise** antes de operar

### Melhorias Futuras
- Integração com APIs de corretoras
- Mais indicadores técnicos
- Machine learning para previsões
- Alertas por email/SMS
- Gráficos interativos
- Análise de múltiplos ativos

## 📞 Suporte

Esta plataforma foi desenvolvida como uma solução completa e robusta para análise de mini dólar. Para dúvidas ou melhorias, consulte o código-fonte ou a documentação das APIs.

---

**⚠️ Aviso Legal**: Esta plataforma é apenas para fins educacionais e informativos. Não constitui aconselhamento financeiro. Sempre consulte um profissional qualificado antes de tomar decisões de investimento.

