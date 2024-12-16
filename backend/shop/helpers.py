from shop.models import Order, Transaction


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
