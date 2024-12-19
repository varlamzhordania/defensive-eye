import stripe

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(_("email address"), blank=True, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name=_("Phone Number"))
    wallet = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        verbose_name=_("Wallet"),
        validators=[MinValueValidator(0)]
    )
    last_ip = models.GenericIPAddressField(verbose_name=_("Last IP Address"), null=True, blank=True)
    stripe_customer_id = models.CharField(verbose_name=_("Stripe Customer ID"), max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        if not self.first_name and not self.last_name:
            return self.username
        return f"{self.first_name} {self.last_name}"

    @property
    def get_initials_name(self):
        if not self.first_name or not self.last_name:
            return self.username[0:2]
        return f"{self.first_name[0]}{self.last_name[0]}"

    @property
    def get_wallet_display(self):
        return f"${self.wallet}"

    def has_subscription(self):
        """
        Check if the subscription is active.
        """
        if hasattr(self, "subscription"):
            return self.subscription.status in ['active', 'trialing']
        return False


class Subscription(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    plan = models.ForeignKey('main.Plans', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, default='active')

    def __str__(self):
        return f"{self.user.get_full_name} - {self.plan.name}"

    def cancel(self):
        if not self.stripe_subscription_id:
            raise ValueError("No subscription to cancel.")

        try:
            stripe.Subscription.cancel(
                self.stripe_subscription_id,
            )
            self.status = 'canceled'
            self.save(update_fields=['status'])

            return True
        except stripe.error.StripeError as e:
            raise ValueError(f"Failed to cancel subscription: {str(e)}")


class Contacts(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"), related_name="contacts")
    name = models.CharField(verbose_name=_("Name"), max_length=100, help_text=_("Name of contact"))
    phone_number = PhoneNumberField(
        verbose_name=_("Phone Number"),
        help_text=_('Enter a valid phone number.')
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ("-created_at", "name")

    def __str__(self):
        return self.name + " " + self.phone_number
