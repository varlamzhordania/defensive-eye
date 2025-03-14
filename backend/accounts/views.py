from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, LoginForm, ContactForm, CustomUserChangeForm, CustomChangePasswordForm
from .decorators import unauthenticated_user
from .models import Contacts

from main.models import Plans
from core.utils import fancy_message


def user_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    form = CustomUserChangeForm(instance=request.user)
    password_form = CustomChangePasswordForm(user=request.user)

    if request.method == "POST":
        form = CustomUserChangeForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            fancy_message(request, "You have successfully changed your account.", "success")
            return redirect(".")
        else:
            fancy_message(request, "Please make sure to fill fields correctly.", "error")
            print(form.errors)
    context = {
        "active_tab": "account",
        "title": "Account | Eye Security",
        "form": form,
        "password_form": password_form,
    }
    return render(request, 'accounts/account.html', context)


@login_required
@require_POST
def password_change_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    form = CustomChangePasswordForm(user=request.user, data=request.POST)
    if form.is_valid():
        form.save()
        fancy_message(request, "You have successfully changed your password.", "success")
        return redirect("accounts:user_edit")
    else:
        fancy_message(request, form.errors, "error")
        return redirect("accounts:user_edit")


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
            login(request, user, backend='accounts.backends.EmailBackend')
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


@login_required
def contact_list_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    contacts = Contacts.objects.filter(user=request.user, is_active=True)

    paginator = Paginator(contacts, 10)
    page = request.GET.get('page', 1)

    paged_contacts = paginator.get_page(page)

    context = {
        "active_tab": "contacts",
        "title": "Contact list",
        "contacts": paged_contacts,
    }

    if request.htmx:
        return render(request, "accounts/components/contact_list_result.html", context)

    return render(request, "accounts/contact_list.html", context)


@login_required
def contact_create_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            fancy_message(request, "New contact added successfully.", "success")
            return redirect("accounts:contact_list")
        else:
            fancy_message(request, "Resolve the errors and try again.", "error")
    context = {
        "active_tab": "contacts",
        "title": "Contact list",
        "form": form,
    }
    return render(request, "accounts/contact_create.html", context)


@login_required
def contact_delete_view(request: HttpRequest, contact_id, *args, **kwargs) -> HttpResponse:
    contact = get_object_or_404(Contacts, id=contact_id, user=request.user)
    contact.delete()
    fancy_message(request, "Contact deleted successfully.", "success")
    return redirect("accounts:contact_list")


@login_required
def subscription_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    plans = Plans.objects.filter(is_active=True).order_by("created_at")

    context = {
        "active_tab": "subscriptions",
        "title": "Subscription plans",
        "plans": plans,
    }

    return render(request, 'accounts/subscription_list.html', context)


@login_required
def cancel_subscription_view(request):
    user = request.user

    if not hasattr(user, 'subscription'):
        fancy_message(request, "You have no subscription yet.", "error")
        return redirect("accounts:subscription_list")

    try:
        user.subscription.cancel()
        fancy_message(request, "Subscription canceled successfully.", "success")
        return redirect("accounts:subscription_list")
    except ValueError as e:
        fancy_message(request, "Something went wrong.please try later.", "error")
        print("cancel subscription error: {}".format(e))
        return redirect("accounts:subscription_list")
