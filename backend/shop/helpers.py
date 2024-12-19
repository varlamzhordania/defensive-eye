from accounts.models import Subscription
from main.models import Plans
from shop.models import Order, Transaction

from django.contrib.auth import get_user_model


def handle_checkout_session_completed(data):
    """
    Handle Stripe 'checkout.session.completed' events.
    """
    client_reference_id = data.get('client_reference_id')
    payment_intent_id = data.get('payment_intent')

    # Find the associated order
    order = Order.objects.filter(id=client_reference_id).first()
    if not order:
        return

    # Update order status and create a transaction record
    order.update_status(Order.StatusChoices.PENDING)
    Transaction.objects.create(
        order=order,
        transaction_id=payment_intent_id,
        status=Transaction.TransactionStatusChoices.COMPLETED,
        payment_method="Stripe",
        amount=order.total_price,
    )


def handle_payment_intent_succeeded(data):
    """
    Handle Stripe 'payment_intent.succeeded' events.
    """
    payment_intent_id = data.get('id')
    order = Order.objects.filter(stripe_payment_intent_id=payment_intent_id).first()

    if not order:
        return

    # Update the order status
    order.update_status(Order.StatusChoices.PROCESSING)


def handle_payment_intent_failed(data):
    """
    Handle Stripe 'payment_intent.payment_failed' events.
    """
    payment_intent_id = data.get('id')
    order = Order.objects.filter(stripe_payment_intent_id=payment_intent_id).first()

    if not order:
        return

    # Update the order status
    order.update_status(Order.StatusChoices.FAILED)


def handle_payment_intent_canceled(data):
    """
    Handle Stripe 'payment_intent.canceled' events.
    """
    payment_intent_id = data.get('id')
    order = Order.objects.filter(stripe_payment_intent_id=payment_intent_id).first()

    if not order:
        return

    # Update the order status
    order.update_status(Order.StatusChoices.CANCELED)


def handle_subscription_created(data):
    """
    Handle 'customer.subscription.created' event.
    """
    stripe_subscription_id = data.get('id')
    stripe_customer_id = data.get('customer')
    status = data.get('status')
    plan_id = data.get('items', {}).get('data', [{}])[0].get('price', {}).get('id')

    # Find user and plan
    user = get_user_model().objects.filter(stripe_customer_id=stripe_customer_id).first()
    plan = Plans.objects.filter(stripe_price_id=plan_id).first()

    if user and plan:
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            defaults={
                'stripe_subscription_id': stripe_subscription_id,
                'plan': plan,
                'status': status,
                'is_active': True,  # Ensure the subscription is marked as active
            },
        )


def handle_subscription_updated(data):
    """
    Handle 'customer.subscription.updated' event.
    """
    stripe_subscription_id = data.get('id')
    status = data.get('status')

    print(data)

    subscription = Subscription.objects.filter(stripe_subscription_id=stripe_subscription_id).first()
    if subscription:
        subscription.status = status
        subscription.save(update_fields=['status'])


def handle_subscription_deleted(data):
    """
    Handle 'customer.subscription.deleted' event.
    """
    stripe_subscription_id = data.get('id')

    subscription = Subscription.objects.filter(stripe_subscription_id=stripe_subscription_id).first()
    if subscription:
        subscription.status = 'canceled'
        subscription.save(update_fields=['status'])
