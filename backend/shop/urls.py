from django.urls import path

from shop import views

app_name = 'shop'

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/update/', views.update_cart_item_view, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('stripe/create-session/<int:order_id>/', views.create_stripe_session_view, name='stripe_create_session'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
]
