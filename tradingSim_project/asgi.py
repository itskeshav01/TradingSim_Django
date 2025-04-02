"""
ASGI config for tradingSim_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import websocket_app.routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tradingSim_project.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # Handles HTTP requests
        "websocket": URLRouter(websocket_app.routing.websocket_urlpatterns),  # Handles WebSocket requests
    }
)
