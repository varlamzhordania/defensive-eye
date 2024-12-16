import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):

    class Meta:
        model = ShippingAddress
        exclude = ('order', 'is_active')

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].required = True

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')

        # Example 1: Validate length
        if len(postal_code) < 4 or len(postal_code) > 10:
            raise ValidationError(_("Postal code must be between 4 and 10 characters."))

        # Example 2: Validate alphanumeric format
        if not re.match(r'^[A-Za-z0-9\- ]+$', postal_code):
            raise ValidationError(_("Postal code can only contain letters, numbers, hyphens, and spaces."))

        # Example 3: Country-specific format validation
        country = self.cleaned_data.get('country')
        if country == 'US' and not re.match(r'^\d{5}(-\d{4})?$', postal_code):
            raise ValidationError(_("US postal code must be 5 digits or in ZIP+4 format (e.g., 12345 or 12345-6789)."))

        if country == 'CA' and not re.match(r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$', postal_code):
            raise ValidationError(_("Canadian postal code must be in the format A1A 1A1."))

        return postal_code
