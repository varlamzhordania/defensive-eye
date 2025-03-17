from django.urls import path
from api.views.cart import CartItemApiView
from api.views.stream import ActiveStreamsView, StreamSessionTimeAnalyticsView, BandwidthUsageAnalyticsView
from api.views.account import subscriptionView

app_name = 'api'

urlpatterns = [
    path('cart/<int:item_id>/', CartItemApiView.as_view(), name='cart_item'),
    path('streams/active_sessions/', ActiveStreamsView.as_view(), name='active_sessions'),
    path('streams/sessions_analytics/', StreamSessionTimeAnalyticsView.as_view(), name='sessions_analytics'),
    path('streams/bandwidth_usage/', BandwidthUsageAnalyticsView.as_view(), name='bandwidth_usage'),
    path('account/subscription/', subscriptionView.as_view(), name='subscription'),
]
