from django.urls import path
from .views import TradeListCreateView, TradeDetailView, fetch_trade_analysis

urlpatterns = [
    path('trades/', TradeListCreateView.as_view(), name='trade-list'),
    path('trades/<int:pk>/', TradeDetailView.as_view(), name='trade-detail'),
      path("trade-analysis/", fetch_trade_analysis, name="fetch_trade_analysis"),
]