import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.asgi import get_asgi_application
app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from websocket.router import urlpatterns

application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": AuthMiddlewareStack(
            URLRouter(urlpatterns)
        ),
    }
)
