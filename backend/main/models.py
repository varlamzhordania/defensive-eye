import stripe

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.conf import settings
from autoslug import AutoSlugField

from core.models import BaseModel, UploadPath

stripe.api_key = settings.STRIPE_SECRET_KEY


class Plans(BaseModel):
    class QualityChoices(models.TextChoices):
        LOW = "Low", _("320p")
        MEDIUM = "Medium", _("480p")
        HD = "HD", _("720p")
        FULL_HD = "Full-HD", _("1080p")
        ULTRA_HD = "Ultra-HD", _("4K")

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        unique=True
    )
    slug = AutoSlugField(
        verbose_name=_('Slug'),
        populate_from='name',
        unique=True,
        blank=True
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        default='',
        help_text=_('Provide a brief description of the plan')
    )
    max_fps = models.PositiveIntegerField(default=10, verbose_name=_('Max FPS'), help_text=_('Max FPS Camera streams'))
    quality = models.CharField(verbose_name=_("Quality"), max_length=10, choices=QualityChoices.choices,
                               default=QualityChoices.MEDIUM)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Price'),
        help_text=_('Price per cycle. Set the price for 31 days (monthly), the system multiplies it for yearly plans.'),
        validators=[MinValueValidator(0, message=_('Price must be a positive value'))]
    )
    items = models.ManyToManyField(
        "PlansItem",
        verbose_name=_('Items'),
        blank=True,
        related_name="plans"
    )
    stripe_product_id = models.CharField(verbose_name=_("Stripe Product ID"), max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(verbose_name=_("Stripe Product ID"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Plan')
        verbose_name_plural = _('Plans')
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name

    def _create_stripe(self):
        if self.stripe_product_id and self.stripe_price_id:
            print("Stripe product and price already exist.")
            return

        product = stripe.Product.create(name=self.name, description=self.description)

        price = stripe.Price.create(
            unit_amount=int(self.price * 100),  # Stripe uses cents
            currency='usd',
            recurring={'interval': 'month'},  # Monthly billing
            product=product['id'],
        )
        self.stripe_product_id = product['id']
        self.stripe_price_id = price['id']
        self.save(update_fields=['stripe_product_id', 'stripe_price_id'])

    def get_items(self):
        return self.items.filter(is_active=True)


class PlansItem(BaseModel):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )
    description = models.CharField(
        max_length=255,
        verbose_name=_('Description'),
        default='',
        help_text=_('This will appear as item text on plans.')
    )

    class Meta:
        verbose_name = _('Plans Item')
        verbose_name_plural = _('Plans Items')
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name


class Products(BaseModel):
    class TypeChoices(models.TextChoices):
        PERSONAL = "PERSONAL", _("Personal")
        HOME = "HOME", _("Home")
        COMPANY = "COMPANY", _("Company")

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        unique=True,
    )
    slug = AutoSlugField(
        populate_from='name',
        verbose_name=_('Slug'),
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        default='',
        help_text=_('Provide a detailed description of the product.')
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=15,
        choices=TypeChoices.choices,
        default=TypeChoices.PERSONAL,
        help_text=_('The type of product.')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Price'),
        validators=[MinValueValidator(0, message=_('Price must be a positive value'))],
        help_text=_('Price of the product. Ensure this is set correctly.')
    )

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("main:product", kwargs={"slug": self.slug})

    def get_price(self):
        return self.price

    def get_display_price(self):
        return f"${self.get_price():.2f}"

    def get_featured_media(self):
        queryset = self.media.all()
        featured_medias = queryset.filter(is_featured=True)
        if featured_medias.exists():
            return featured_medias.first().image.url

        return queryset.first().image.url


class ProductStock(BaseModel):
    product = models.OneToOneField(Products, verbose_name=_('Product'), on_delete=models.CASCADE, related_name='stock')
    total_stock = models.PositiveIntegerField(
        verbose_name=_('Total Stock'),
        default=0,
        validators=[MinValueValidator(0, message=_('Total Stock must be a positive value'))]
    )
    total_sold = models.PositiveIntegerField(
        verbose_name=_('Total Sold'),
        default=0,
        validators=[MinValueValidator(0, message=_('Total Sold must be a positive value'))]
    )

    class Meta:
        verbose_name = _('Product Stock')
        verbose_name_plural = _('Product Stocks')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - stock"

    @property
    def available_stock(self):
        return self.total_stock - self.total_sold

    @property
    def is_available(self):
        return self.available_stock > 0

    def sold(self, amount):
        if amount <= self.available_stock:
            self.total_sold += amount
            self.save(update_fields=['total_sold'])
        else:
            raise ValueError(_("Not enough stock available"))


class ProductMedia(BaseModel):
    product = models.ForeignKey(Products, verbose_name=_('Product'), on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(
        upload_to=UploadPath(folder="products", sub_path="medias"), verbose_name=_("Image"),
    )
    is_featured = models.BooleanField(verbose_name=_('Is featured?'), default=False)

    class Meta:
        verbose_name = _('Product Media')
        verbose_name_plural = _('Product Medias')
        ordering = ['-created_at', 'is_featured']

    def __str__(self):
        return f"{self.product.name} - Media"


class ProductRegistered(BaseModel):
    product = models.ForeignKey(
        Products,
        verbose_name=_('Product'),
        on_delete=models.CASCADE,
        related_name='registered'
    )
    code = models.CharField(max_length=64, verbose_name=_('Code'), unique=True, db_index=True)
    is_claimed = models.BooleanField(verbose_name=_('Is claimed?'), default=False)
    claimed_user = models.ForeignKey(
        get_user_model(),
        verbose_name=_('Claimed User'),
        on_delete=models.CASCADE,
        related_name='claimed_products',
        null=True,
        blank=True,
        help_text=_('The user who claimed or activated the product.')
    )

    class Meta:
        verbose_name = _('Product Registered')
        verbose_name_plural = _('Product Registered')
        ordering = ['-created_at', 'is_claimed']

    def __str__(self):
        if self.is_claimed:
            return f"{self.product.name} - Claimed by {self.claimed_user.username} - Code #{self.code}"
        return f"{self.product.name} - Code #{self.code} (Unclaimed)"

    def claim_product(self, user):
        if self.is_claimed:
            raise ValueError(_("This product has already been claimed."))
        self.claimed_user = user
        self.is_claimed = True
        self.save(update_fields=['claimed_user', 'is_claimed'])
