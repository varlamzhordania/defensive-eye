from django.urls import path
from .views import login_view, registration_view,logout_view

app_name = 'accounts'

urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', registration_view, name='register'),
    path('auth/logout/', logout_view, name='logout'),
]
