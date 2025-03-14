from django.urls import path
from .views import home_view, dashboard_view, product_view, camera_list_view

app_name = 'main'

urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('product/<slug:slug>/', product_view, name='product'),
    path('dashboard/cameras/', camera_list_view, name='cameras_list'),

]
