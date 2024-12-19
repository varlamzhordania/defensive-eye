from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.registration_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),

    path('dashboard/account/', views.user_view, name='user_edit'),
    path('dashboard/contacts/', views.contact_list_view, name='contact_list'),
    path('dashboard/contacts/create/', views.contact_create_view, name='contact_create'),
    path('dashboard/contact/<int:contact_id>/delete/', views.contact_delete_view, name='contact_delete'),
    path('dashboard/subscriptions/', views.subscription_view, name='subscription_list'),
    path('dashboard/subscriptions/cancel/', views.cancel_subscription_view, name='cancel_subscription'),
]
