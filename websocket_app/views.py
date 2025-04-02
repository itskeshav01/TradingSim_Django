# views.py
from django.shortcuts import render

def stock_monitor(request):
    return render(request, 'index.html')
