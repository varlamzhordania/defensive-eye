from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, LoginForm
from .decorators import unauthenticated_user

from core.utils import fancy_message


# Create your views here.

@unauthenticated_user
def login_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    form = LoginForm()
    next_url = request.GET.get('next', None)
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='accounts.backends.EmailBackend')
            fancy_message(request, "Welcome {}".format(user.username), "success")
            if next_url:
                return redirect(next_url)
            return redirect("main:dashboard")
        else:
            fancy_message(request, "Invalid username or password.", "error")
    context = {
        "title": "Sign In to defensive eye account",
        "form": form,
    }
    return render(request, "accounts/login.html", context)


@unauthenticated_user
def registration_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            fancy_message(request, "Welcome {}".format(user.username), "success")
            return redirect("main:dashboard")
        else:
            fancy_message(request, form.errors, "error")
    context = {
        "title": "Sign up in defensive eye",
        "form": form,
    }
    return render(request, "accounts/register.html", context)


@login_required
def logout_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    logout(request)
    fancy_message(request, "You have been logged out successfully.", "success")

    return redirect("main:home")
