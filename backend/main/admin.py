from django.contrib import admin
from .models import Products, ProductMedia, ProductStock, ProductRegistered


admin.site.register(Products)
admin.site.register(ProductMedia)
admin.site.register(ProductStock)
admin.site.register(ProductRegistered)
