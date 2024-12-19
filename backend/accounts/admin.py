from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import User, Contacts, Subscription


class CustomUserResource(resources.ModelResource):
    class Meta:
        model = User


class SubscriptionInline(admin.StackedInline):
    model = Subscription


@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    model = User
    list_display = (
        "id", "username", "email", "wallet", "is_staff", "is_superuser", "is_active", "date_joined",
        "last_login")
    list_filter = ("is_staff", "is_active", "groups")
    readonly_fields = ("date_joined", "last_login", "last_ip", "stripe_customer_id")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Information",
         {"fields": ("first_name", "last_name", "email", "phone_number", "wallet", "stripe_customer_id")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
        ("Security", {"fields": ("date_joined", "last_login", "last_ip")}),
    )
    add_fieldsets = (
        (None, {
            "fields": (
                "username", "email", "password1", "password2",
                "groups", "is_staff", "is_active",
            )}
         ),
    )
    search_fields = ("id", "username", "email",)
    ordering = ("id",)
    resource_classes = [CustomUserResource]
    inlines = [SubscriptionInline]


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone_number', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('user', 'name', 'phone_number')
