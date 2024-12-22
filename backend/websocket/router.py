from django.urls import path
from .views import UserStreamConsumer, CameraStreamConsumer

urlpatterns = [
    path('ws/camera_stream/', CameraStreamConsumer.as_asgi()),
    path('ws/view_stream/', UserStreamConsumer.as_asgi()),
]
