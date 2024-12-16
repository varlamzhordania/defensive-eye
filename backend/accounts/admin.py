from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import User


class CustomUserResource(resources.ModelResource):
    class Meta:
        model = User


class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    model = User
    list_display = (
        "id", "username", "email", "wallet", "is_staff", "is_superuser", "is_active", "date_joined",
        "last_login")
    list_filter = ("is_staff", "is_active", "groups")
    readonly_fields = ("date_joined", "last_login", "last_ip")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Information",
         {"fields": ("first_name", "last_name", "email", "phone_number", "wallet")}),
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


admin.site.register(User, CustomUserAdmin)