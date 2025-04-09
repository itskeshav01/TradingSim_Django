from rest_framework import generics
from .models import Trade
from .serializers import TradeSerializer
import requests
from django.http import JsonResponse
from django.conf import settings
import yfinance as yf
from rest_framework.views import APIView
from rest_framework.response import Response
import math
# Handles GET (list all trades) and POST (create a trade)
class TradeListCreateView(generics.ListCreateAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    
    def get_queryset(self):
        queryset = Trade.objects.all()
        
        # Filter by ticker if provided
        ticker = self.request.query_params.get('ticker', None)
        if ticker:
            queryset = queryset.filter(ticker=ticker.upper())
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
                
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
                
        return queryset

# Handles GET (single trade), PUT/PATCH (update) and DELETE (remove)
class TradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer



def fetch_trade_analysis(request):
    """Django API to call AWS Lambda function"""
    date = request.GET.get("date", None)
    
    if not date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    lambda_url = settings.AWS_LAMBDA_API_URL
    params = {"date": date}

    try:
        response = requests.get(lambda_url, params=params)
        data = response.json()
        return JsonResponse(data)
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    

class TopStocksView(APIView):
    def get(self, request):
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", 
                   "TSLA", "NVDA", "BRK-B", "JPM", "V", 
                   "JNJ", "PG", "MA", "HD", "DIS"]

        response_data = []

        for ticker in tickers:
            try:
                data = yf.Ticker(ticker).history(period="1d", interval="1m")

                if data.empty:
                    raise ValueError("No data found")

                open_price = data["Open"].iloc[0]
                close_price = data["Close"].iloc[-1]

                # Sanitize data
                if not all(map(lambda x: isinstance(x, (int, float)) and math.isfinite(x), [open_price, close_price])):
                    raise ValueError("Invalid price values")

                change = close_price - open_price
                percent_change = (change / open_price) * 100

                response_data.append({
                    "ticker": ticker,
                    "price": round(close_price, 2),
                    "change": round(change, 2),
                    "percent_change": round(percent_change, 2)
                })

            except Exception as e:
                response_data.append({
                    "ticker": ticker,
                    "error": str(e)
                })

        return Response(response_data)