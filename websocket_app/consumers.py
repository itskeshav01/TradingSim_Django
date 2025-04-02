import json
import asyncio
import yfinance as yf
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from tradingSim_app.models import StockPrice  # Import the model

class StockPriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles new WebSocket connection."""
        self.ticker = self.scope["url_route"]["kwargs"]["ticker"]
        await self.accept()  # Accept WebSocket connection
        await self.send(json.dumps({"message": f"Connected to {self.ticker} WebSocket"}))

        # Start streaming stock prices
        await self.stream_stock_data()

    async def stream_stock_data(self):
        """Fetch real-time stock data and send updates to WebSocket clients."""
        last_price = None
        self.connected = True

        while self.connected:
            data = await self.get_real_stock_data()
            await self.send(json.dumps(data))

            # Save data to the database
            await self.save_to_db(data)

            # Trigger alert if price changes by more than 2%
            if last_price and abs((data["price"] - last_price) / last_price) * 100 > 2:
                await self.send(json.dumps({"alert": "Stock price changed more than 2%!"}))

            last_price = data["price"]
            await asyncio.sleep(1)  # Wait for 1 second before fetching new data

    async def get_real_stock_data(self):
        stock = yf.Ticker(self.ticker)
        history_data = stock.history(period="1d", interval="1m")
        if history_data.empty:
            return {
                "ticker": self.ticker,
                "price": 0.0,
                "timestamp": self.get_timestamp(),
                "error": f"No data found for {self.ticker}"
            }
        data = history_data.iloc[-1]
        return {
            "ticker": self.ticker,
            "price": round(data["Close"], 2),
            "timestamp": self.get_timestamp(),
        }

    async def save_to_db(self, data):
        """Save stock data to the database."""
        ma_5min = await self.calculate_moving_average(data["ticker"])
        await sync_to_async(StockPrice.objects.create)(
            ticker=data["ticker"], 
            price=data["price"], 
            timestamp=data["timestamp"],
            moving_average_5min=ma_5min
        )
    async def calculate_moving_average(self, ticker):
        from datetime import datetime, timedelta
        from django.utils.timezone import now

        five_minutes_ago = now() - timedelta(minutes=5)
        
        recent_prices = await sync_to_async(list)(
            StockPrice.objects.filter(ticker=ticker, timestamp__gte=five_minutes_ago)
            .order_by("-timestamp")
            .values_list("price", flat=True)
        )
        if recent_prices:
            return round(sum(recent_prices) / len(recent_prices), 2)
        return None

    def get_timestamp(self):
        """Generate a formatted timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection properly."""
        print(f"Disconnected: {close_code}")
        self.connected = False  # Stop the loop
