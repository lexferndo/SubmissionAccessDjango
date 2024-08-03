# your_project_name/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dash.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add other protocol types here if needed
})
