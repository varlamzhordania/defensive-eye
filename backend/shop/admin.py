from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, Transaction

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('total_price',)

    def total_price(self, obj):
        return obj.get_display_price()


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('cart', 'product')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    search_fields = ('user__username', 'user__email', 'id')
    list_filter = ('status', 'created_at', 'updated_at')
    readonly_fields = ('total_price', 'stripe_payment_intent_id')

    def total_price(self, obj):
        return f"${obj.total_price:.2f}"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'total_price')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('order', 'product')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'email', 'city', 'country')
    search_fields = ('order__user__username', 'full_name', 'email', 'city')
    list_filter = ('country', 'created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'status', 'payment_method', 'amount', 'created_at')
    search_fields = ('transaction_id', 'order__user__username', 'order__id')
    list_filter = ('status', 'payment_method', 'created_at', 'updated_at')
    raw_id_fields = ('order',)
