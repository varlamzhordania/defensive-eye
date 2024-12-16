from django.urls import path
from .views import CartItemApiView

app_name = 'api'

urlpatterns = [
    path('cart/<int:item_id>/', CartItemApiView.as_view(), name='cart_item'),
]
