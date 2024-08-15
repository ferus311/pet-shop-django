import re
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .constants import (MAX_LENGTH_NAME, MAX_LENGTH_PASSWORD, REGEX_USERNAME,
                        REGEX_USERNAME, REGEX_PHONENUM, REGEX_EMAIL)
from django.contrib.auth.forms import UserCreationForm


class SignInForm(forms.Form):
    username = forms.CharField(max_length=MAX_LENGTH_NAME)
    password = forms.CharField(
        max_length=MAX_LENGTH_PASSWORD, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.search(REGEX_USERNAME, username):
            raise forms.ValidationError(
                _("Username can only contain alphanumeric characters and the underscore."))
        return username


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email',
                  'username', 'password1', 'password2',
                  'default_phone_number', 'default_address')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_pattern = re.compile(REGEX_EMAIL)
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("A user with that email already exists."))
        if not re.search(email_pattern, email):
            raise forms.ValidationError(_("Email invalid."))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _("A user with that username already exists."))
        if not re.search(REGEX_USERNAME, username):
            raise forms.ValidationError(
                _("Username can only contain alphanumeric characters and the underscore."))
        return username

    def clean_phone_num(self):
        phone_num = self.cleaned_data.get('default_phone_number')
        phone_pattern = re.compile(REGEX_PHONENUM)
        if not phone_pattern.match(phone_num):
            raise forms.ValidationError(
                _("Phone number must be 10 digits and start with 0."))
        return phone_num

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        if commit:
            user.save()
        return user
