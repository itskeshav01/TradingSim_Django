# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('monitor/', views.stock_monitor, name='stock_monitor'),
]
