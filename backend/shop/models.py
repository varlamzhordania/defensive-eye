from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

from core.models import BaseModel
from main.models import Products


class Cart(BaseModel):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("User"),
    )

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def get_display_price(self):
        return f"${self.total_price:.2f}"

    def clear_cart(self):
        self.items.all().delete()


class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Cart"),
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1, message=_("Quantity must be at least 1"))],
        verbose_name=_("Quantity"),
    )

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in {self.cart.user.username}'s cart"

    @property
    def total_price(self):
        return Decimal(self.quantity) * self.product.price

    def get_display_price(self):
        return f"${self.total_price:.2f}"

    def increase_quantity(self, amount):
        self.quantity += amount
        self.save(update_fields=["quantity"])

    def decrease_quantity(self, amount):
        self.quantity -= amount
        self.save(update_fields=["quantity"])


class Order(BaseModel):
    class StatusChoices(models.TextChoices):
        WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT", _("Waiting for Payment")
        PENDING = "PENDING", _("Pending")
        PROCESSING = "PROCESSING", _("Processing")
        SENT_SHIPPING = "SENT_SHIPPING", _("Sent Shipping")
        COMPLETED = "COMPLETED", _("Completed")
        FAILED = "FAILED", _("Failed")
        CANCELED = "CANCELED", _("Canceled")

    user = models.ForeignKey(
        get_user_model(),
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.WAITING_FOR_PAYMENT,
        verbose_name=_('Order Status')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Price')
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        verbose_name=_('Stripe Payment Intent ID'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.get_status_display()}"

    def calculate_total_price(self):
        total = sum(item.total_price for item in self.items.filter(is_active=True))
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total

    def update_status(self, new_status):
        self.status = new_status
        self.save(update_fields=["status"])


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Products,
        verbose_name=_('Product'),
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantity')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Total Price')
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class ShippingAddress(BaseModel):
    order = models.OneToOneField(
        Order,
        verbose_name=_('Order'),
        on_delete=models.CASCADE,
        related_name='shipping_address',
        help_text=_('The associated order for this shipping address.')
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name=_('Receiver Full Name'),
        help_text=_('Enter the full name of the person receiving the shipment.')
    )
    email = models.EmailField(
        verbose_name=_('Receiver Email'),
        help_text=_('Enter the email address of the person receiving the shipment.')
    )
    address_line1 = models.CharField(
        max_length=255,
        verbose_name=_('Address Line 1'),
        help_text=_('Enter the primary street address (e.g., 123 Main St).')
    )
    address_line2 = models.CharField(
        max_length=255,
        verbose_name=_('Address Line 2'),
        blank=True,
        null=True,
        help_text=_('Enter additional address information (e.g., Apartment, Suite, Unit), if applicable.')
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_('City'),
        help_text=_('Enter the city for the shipping address.')
    )
    state = models.CharField(
        max_length=100,
        verbose_name=_('State/Province'),
        help_text=_('Enter the state or province for the shipping address.')
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_('Postal Code'),
        help_text=_('Enter the postal or ZIP code for the shipping address.')
    )
    country = CountryField(
        verbose_name=_('Country'),
        blank_label='Select Country',
        help_text=_('Enter the country for the shipping address.')
    )
    phone_number = PhoneNumberField(
        verbose_name=_('Phone Number'),
        blank=True,
        null=True,
        help_text=_('Enter a valid phone number for the recipient.')
    )

    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")
        ordering = ("-country",)

    def __str__(self):
        return f"Shipping Address for Order #{self.order.id}"


class Transaction(BaseModel):
    class TransactionStatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        COMPLETED = "COMPLETED", _("Completed")
        FAILED = "FAILED", _("Failed")
        REFUNDED = "REFUNDED", _("Refunded")

    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_id = models.CharField(
        max_length=255,
        verbose_name=_('Transaction ID'),
        unique=True
    )
    status = models.CharField(
        max_length=15,
        choices=TransactionStatusChoices.choices,
        default=TransactionStatusChoices.PENDING,
        verbose_name=_('Transaction Status')
    )
    payment_method = models.CharField(
        max_length=50,
        verbose_name=_('Payment Method'),
        blank=True,
        null=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Transaction Amount')
    )

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.get_status_display()} - Order #{self.order.id}"
