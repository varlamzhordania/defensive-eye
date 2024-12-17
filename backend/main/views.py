from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse

from main.models import Products, ProductRegistered


def home_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    context = {
        "active_tab": "home",
        "title": "Defensive Eye Security",
    }
    return render(request, "main/home.html", context)


def product_view(request: HttpRequest, slug, *args, **kwargs) -> HttpResponse:
    product = get_object_or_404(Products, slug=slug)
    context = {
        "active_tab": "products",
        "title": product.name,
        "product": product,
    }

    return render(request, "main/product.html", context)


@login_required
def dashboard_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    context = {
        "title": "Dashboard | Defensive Eye Security",
    }
    return render(request, "main/dashboard.html", context)


def camera_list_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    context = {}

    return render(request)
