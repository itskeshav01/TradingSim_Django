from django.urls import path
from .views import TradeListCreateView, TradeDetailView, fetch_trade_analysis, TopStocksView

urlpatterns = [
    path('trades/', TradeListCreateView.as_view(), name='trade-list'),
    path('trades/<int:pk>/', TradeDetailView.as_view(), name='trade-detail'),
    path("trade-analysis/", fetch_trade_analysis, name="fetch_trade_analysis"),
    path("top-stocks/", TopStocksView.as_view(), name="top-stocks"), 
]