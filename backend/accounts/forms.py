from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from .models import User, Contacts


class CustomChangePasswordForm(PasswordChangeForm):
    pass


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ("username", "email", "is_staff", "is_active", "is_superuser", "groups", "user_permissions","date_joined","wallet")


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        exclude = ('user', 'is_active')


class LoginForm(AuthenticationForm):
    email = forms.EmailField(required=True, label=_("Email"), widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if (username is not None or email is not None) and password:
            if username:
                self.user_cache = authenticate(
                    self.request, username=username, password=password
                )
            else:
                self.user_cache = authenticate(
                    self.request, email=email, password=password
                )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text=_("Required. Enter a valid email address."),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "example@example.com"})
    )

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "password1", "password2"
        )
        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _("Enter your first name here")}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _("Enter your last name here")}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user
