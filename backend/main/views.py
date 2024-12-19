from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse

from main.models import Products, ProductRegistered, Plans


def home_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    plans = Plans.objects.filter(is_active=True)
    context = {
        "active_tab": "home",
        "title": "Defensive Eye Security",
        "plans": plans,
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
        "active_tab": "dashboard",
        "title": "Dashboard | Defensive Eye Security",
    }
    return render(request, "main/dashboard.html", context)


@login_required
def camera_list_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    cameras = ProductRegistered.objects.filter(claimed_user=request.user)

    paginator = Paginator(cameras, 10)
    page = request.GET.get('page', 1)

    paged_cameras = paginator.get_page(page)

    context = {
        "active_tab": "cameras",
        "title": "Cameras list",
        "cameras": paged_cameras
    }

    if request.htmx:
        return render(request, 'cameras/components/camera_list_result.html')

    return render(request, 'cameras/camera_list.html', context)
