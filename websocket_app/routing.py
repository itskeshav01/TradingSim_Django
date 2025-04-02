from django.urls import re_path
from .consumers import StockPriceConsumer

websocket_urlpatterns = [
    re_path(r"ws/stocks/(?P<ticker>[\w\.\-]+)/$", StockPriceConsumer.as_asgi()),
]
