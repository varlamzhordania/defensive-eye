from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from phonenumber_field.formfields import SplitPhoneNumberField


class LimitedPhoneNumberField(SplitPhoneNumberField):
    class CountryChoices(TextChoices):
        US = 'US', _('United States (+1)')
        CA = 'CA', _('Canada (+1)')

    def prefix_field(self):
        return forms.ChoiceField(choices=self.get_choices(), required=True)

    def get_choices(self):
        return [("", "---------")] + list(self.CountryChoices.choices)
