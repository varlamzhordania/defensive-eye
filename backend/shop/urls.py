from django.urls import path

from shop import views

app_name = 'shop'

urlpatterns = [
    path('dashboard/orders/', views.order_history_view, name='order_history'),
    path('dashboard/order/<int:order_id>/confirmation/', views.order_confirm_view, name='order_confirm'),
    path('dashboard/order/<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),
    path('dashboard/order/<int:order_id>/', views.order_detail_view, name='order_details'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/update/', views.update_cart_item_view, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('stripe/create-session/<int:order_id>/', views.create_stripe_session_view, name='stripe_create_session'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
]
