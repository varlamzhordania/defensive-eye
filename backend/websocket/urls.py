from django.urls import path
from .views import live_stream_view

app_name = 'websocket'

urlpatterns = [
    path('live_stream/<str:code>/', live_stream_view, name='live_stream'),
]