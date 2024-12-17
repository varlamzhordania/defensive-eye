import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.paginator import Paginator

from main.models import Products
from core.utils import fancy_message

from .models import Order, OrderItem, CartItem, Cart, Transaction
from .form import ShippingAddressForm
from .helpers import handle_checkout_session_completed, handle_payment_intent_failed, handle_payment_intent_canceled, \
    handle_payment_intent_succeeded

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def order_history_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    orders = Order.objects.filter(user=request.user)

    paginator = Paginator(orders, 10)
    page = request.GET.get('page', 1)

    paged_orders = paginator.get_page(page)

    context = {
        "title": "Order history",
        "orders": paged_orders,
    }
    if request.htmx:
        return render(request, "shop/components/order_list_result.html", context)

    return render(request, "shop/order_list.html", context)


@login_required
def order_confirm_view(request: HttpRequest, order_id: int, *args, **kwargs) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    context = {
        "title": "Order confirmation",
        "order": order,
    }
    return render(request, "shop/order_confirmation.html", context)


@login_required
def cancel_order_view(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ["CANCELED", "COMPLETED"]:
        order.update_status(Order.StatusChoices.CANCELED)
        fancy_message(request, "Order canceled successfully.")
    else:
        fancy_message(request, "This order cannot be canceled.")
    return redirect('shop:order_history')


@login_required
def order_detail_view(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {"order": order}
    return render(request, "shop/order_detail.html", context)


@login_required
def add_to_cart_view(request: HttpRequest, product_id: int, *args, **kwargs) -> HttpResponseRedirect:
    product = get_object_or_404(Products, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect("shop:cart_detail")


@login_required
def cart_detail_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    cart = Cart.objects.get(user=request.user)
    items = cart.items.filter(is_active=True)
    cart_items_count = items.count()
    context = {
        "title": "Shopping Cart",
        "cart": cart,
        "cart_items": items,
        "cart_items_count": cart_items_count,
    }
    return render(request, "shop/cart_detail.html", context)


@login_required
def update_cart_item_view(request, item_id, *args, **kwargs) -> HttpResponseRedirect:
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get("quantity", 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect("cart_detail")


@login_required
def checkout_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    shipping_form = ShippingAddressForm()
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        fancy_message(request, "Your cart is empty.", "error")
        return redirect("shop:cart_detail")

    if request.method == "POST":
        shipping_form = ShippingAddressForm(request.POST)
        if shipping_form.is_valid():
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(user=request.user)
                cart_items = cart.items.filter(is_active=True)

                # Add cart items to order
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity
                    )

                # Calculate total price
                order.calculate_total_price()

                # Delete cart items after transfer
                cart_items.delete()

                # Save shipping address
                shipping_address = shipping_form.save(commit=False)
                shipping_address.order = order
                shipping_address.save()

                payment_method = request.POST.get("payment_method")

                if payment_method == "stripe":
                    return redirect("shop:stripe_create_session", order_id=order.id)
                else:
                    fancy_message(
                        request,
                        "Invalid payment method have been selected, you can proceed the payment via order list page.",
                        "error"
                    )
        else:
            print("invalid")
            print(shipping_form.errors)

    context = {
        "active_tab": "checkout",
        "title": "Defensive Eye Security",
        "stripe_key": settings.STRIPE_PUBLISHABLE_KEY,
        "shipping_form": shipping_form,
        "cart": cart,
    }
    return render(request, "shop/checkout.html", context)


@login_required
def create_stripe_session_view(request: HttpRequest, order_id: int, *args, **kwargs) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id, user=request.user)

    line_items = []
    for item in order.items.all():
        line_items.append(
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                        'description': item.product.description,
                        'images': [request.build_absolute_uri(item.product.get_featured_media)],

                    },
                    'unit_amount': int(item.product.price * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            }
        )

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        customer_email=order.user.email,
        success_url=request.build_absolute_uri(reverse("shop:order_confirm", kwargs={"order_id": order.id})),
        cancel_url=request.build_absolute_uri(reverse("shop:cart_detail")),
        client_reference_id=str(order.id),
    )

    order.stripe_payment_intent_id = session.payment_intent
    order.save()

    return redirect(session.url)


@csrf_exempt
@require_POST
def stripe_webhook_view(request: HttpRequest) -> JsonResponse:
    """
    Handle Stripe webhook events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})

    if event_type == 'checkout.session.completed':
        handle_checkout_session_completed(data)
    elif event_type == 'payment_intent.succeeded':
        handle_payment_intent_succeeded(data)
    elif event_type == 'payment_intent.payment_failed':
        handle_payment_intent_failed(data)
    elif event_type == 'payment_intent.canceled':
        handle_payment_intent_canceled(data)

    # Return a 200 response to acknowledge receipt of the event
    return JsonResponse({'status': 'success'}, status=200)
