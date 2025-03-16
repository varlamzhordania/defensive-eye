import os
import threading

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.asgi import get_asgi_application
app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from websocket.router import urlpatterns
from websocket.rabbitmq import RabbitMQWorker

# Start RabbitMQ Worker in a background thread
def start_rabbitmq_worker():
    worker = RabbitMQWorker()
    worker.start_worker()

# Run the worker only once when Daphne starts`
worker_thread = threading.Thread(target=start_rabbitmq_worker, daemon=True)
worker_thread.start()

application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": AuthMiddlewareStack(
            URLRouter(urlpatterns)
        ),
    }
)
