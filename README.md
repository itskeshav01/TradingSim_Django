# Trading System - Real-time Stock Data & Analysis Platform
## Video Explanation 
https://drive.google.com/file/d/1I5DEs_9H90sV0GnwdVqSiKOuEUuCh8CV/view?usp=sharing
## Project Overview

This project implements a comprehensive trading system that processes real-time stock data, manages trades through a REST API, integrates with AWS cloud services for data analysis, and includes algorithmic trading simulation capabilities. The system is built using Django and follows modern software development practices to create a scalable and reliable platform for financial technology applications.

### Key Features
- **Trade Management**: REST API for creating and retrieving trade data
- **Real-time Monitoring**: WebSocket implementation for live stock price tracking
- **Cloud Analysis**: AWS integration for serverless data processing
- **Trading Algorithms**: Simulation of trading strategies (Moving Average Crossover)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation and Setup](#installation-and-setup)
3. [Project Structure](#project-structure)
4. [Component 1: REST API](#component-1-rest-api)
5. [Component 2: WebSocket Real-time Data](#component-2-websocket-real-time-data)
6. [Component 3: AWS Integration](#component-3-aws-integration)
7. [Component 4: Algo Trading(MA Stretegy)](#component-4-algo-trading-(MA-Stretegy))
8. [Testing](#testing)
9. [Development Decisions](#development-decisions)

## Prerequisites

- Python 3.8+
- Django 4.0+
- Django REST Framework
- Django Channels
- PostgreSQL or MongoDB
- Redis (for background tasks)
- AWS account with access to S3 and Lambda
- Boto3 Python package
- yfinance Python package

## Installation and Setup

### Clone the Repository
```bash
git clone https://github.com/yourusername/trading-simulation-system.git
cd trading-simulation-system
```

### Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure the Database
Edit `DATABASES` in `tradingSim_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trading_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configure AWS Credentials
In `awscli` or environment variables:
```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = ap-southeast-2
```
In `tradingSim_project/settings.py`:
```python
AWS_LAMBDA_API_URL = "https://9rio214r4j.execute-api.ap-southeast-2.amazonaws.com/Tradingapp"
```

### Configure Django Channels
In `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'channels',
]

ASGI_APPLICATION = 'tradingSim_project.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Start the Server
```bash
python manage.py runserver
```

## Project Structure
```
trading-simulation-system/
├── tradingSim_project/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
├── tradingSim_app/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── management/commands/export_trades.py
├── websocket_app/
│   ├── urls.py
│   ├── consumers.py
│   ├── routing.py
│   └── templates/monitor.html
└── algo_trading/
    ├── urls.py
    ├── views.py
    ├── templates/alo_trading/upload.html
```

## Component 1: REST API

### Overview
- Base URL: `http://localhost:8000/api/`
- Provides endpoints to create, retrieve, update, delete trades

### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trades/` | List trades (filter by `ticker`, `start_date`, `end_date`) |
| POST | `/api/trades/` | Create new trade |
| GET | `/api/trades/<id>/` | Retrieve trade by ID |
| GET | `/api/trades/?ticker=<ticker>&start_date=<date>&end_date=<date>` | Retrieve trade by ticker & dates |

### Example - Create Trade
```json
{
  "ticker": "AAPL",
  "price": 150.75,
  "quantity": 10,
  "side": "buy"
}
```

### Example - Get Trades
`GET /api/trades/?ticker=AAPL&start_date=2025-01-01&end_date=2025-01-15`

## Component 2: WebSocket Real-time Data

### Running
```bash
http://localhost:8000/web/monitor
```

### Features
- Connect to live stock data using Yahoo Finance
- Real-time updates in browser
- Alerts on 2%+ price changes within 1 minute
- 5-minute moving average tracking

### WebSocket URL Format
```
ws://localhost:8000/ws/stocks/<ticker>/
```

## Component 3: AWS Integration

### Export Trades to S3
```bash
python manage.py export_trades
```
- Exports DB trades to `YEAR/MONTH/DAY/trades.csv` in S3

### Analyze Trade Data (Lambda)
```bash
http://localhost:8000/api/trade-analysis/?date=2025-01-20
```
Triggers Lambda → Analyzes CSV in S3 → Saves result → Returns status

#### Expected Output
```json
{
  "statusCode": 200,
  "message": "Analysis saved for 2025-01-20"
}
```
## Component 4: Algo Trading(MA Stretegy)
### Export Trades to S3
```bash
python stock_price_generator.py
```
- Creates a file in the format: `Date,Open,High,Low,Close,Volume` 
### Upload CSV via Web UI
```bash
http://localhost:8000/algo_trading/
```
- Opens the index.html template where you can upload the generated CSV.
- Backend runs 50/200 MA crossover strategy on the uploaded file.
### Download Trade Analysis
- After upload, use the Download button in the UI
    or directly visit:
```bash
http://localhost:8000/algo_trading/download/
```
- Returns a CSV with Buy/Sell signals, P&L, and total summary.

### Expected Output Format
```
Date, Signal, Price, Profit/Loss
2025-01-02, Buy, 104.5,
2025-01-10, Sell, 110.3, 5.8

 ```
## Testing

### REST API
```bash
curl http://localhost:8000/api/trades/
curl -X POST http://localhost:8000/api/trades/ \
  -H "Content-Type: application/json" \
  -d '{"ticker":"MSFT","price":350.25,"quantity":5,"side":"buy"}'
```

### WebSocket
- Use browser to connect to monitor page
- Enter ticker, click connect

## Development Decisions
- Django for rapid prototyping and scalability
- Channels for asynchronous WebSocket support
- S3 and Lambda for scalable, event-driven analysis
- yfinance for lightweight market data

---

Built with ❤️ using Django, Channels, AWS, and a passion for fintech innovation.

