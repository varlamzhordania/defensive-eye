from django.contrib import admin
from .models import (
    Plans, PlansItem, Products, ProductStock, ProductMedia, ProductRegistered
)


class PlansItemInline(admin.TabularInline):
    model = Plans.items.through
    extra = 1
    verbose_name = "Plan Item"
    verbose_name_plural = "Plan Items"


@admin.action(description="Create Stripe products and prices for selected plans")
def create_stripe_products(modeladmin, request, queryset):
    for plan in queryset:
        try:
            plan._create_stripe()
            modeladmin.message_user(request, f"Stripe details created for {plan.name}")
        except Exception as e:
            modeladmin.message_user(
                request, f"Failed to create Stripe details for {plan.name}: {e}", level="error"
            )


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stripe_product_id', 'stripe_price_id', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('price',)
    # inlines = [PlansItemInline]
    filter_horizontal = ('items',)
    actions = [create_stripe_products]


@admin.register(PlansItem)
class PlansItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    verbose_name = "Product Media"
    verbose_name_plural = "Product Media"


class ProductStockInline(admin.StackedInline):
    model = ProductStock
    extra = 0
    verbose_name = "Stock"
    verbose_name_plural = "Stock"


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'type')
    list_filter = ('type', 'price')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductMediaInline, ProductStockInline]


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'total_stock', 'total_sold', 'available_stock', 'is_available', 'created_at', 'updated_at')
    search_fields = ('product__name',)
    list_filter = ('total_stock', 'total_sold')


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_featured', 'created_at', 'updated_at')
    search_fields = ('product__name',)
    list_filter = ('is_featured',)


@admin.register(ProductRegistered)
class ProductRegisteredAdmin(admin.ModelAdmin):
    list_display = ('product', 'code', 'is_claimed', 'claimed_user', 'created_at', 'updated_at')
    search_fields = ('product__name', 'code', 'claimed_user__username')
    list_filter = ('is_claimed',)
    readonly_fields = ('is_claimed', 'claimed_user')
