import re
import pyotp
from .models import CustomUser
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Product, ProductDetail, Bill, Voucher, VoucherHistory, Category
from .constants import (MAX_LENGTH_NAME, MAX_LENGTH_PASSWORD, REGEX_USERNAME,
                        REGEX_USERNAME, REGEX_PHONENUM, REGEX_EMAIL)
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth import login, authenticate, get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from .widgets import ImagePreviewWidget, DateTimePickerWidget
from .models import Comment
from .models import Bill, PAYMENT_STATUS_CHOICES
from .constants import REGEX_PHONENUM


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
        user.is_active = False
        if commit:
            user.save()
        return user


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES, required=False)
    created_at = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date'}))
    expired_at = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date'}))

    def filter(self, user):
        orders = Bill.objects.filter(user=user)
        if self.cleaned_data['status']:
            orders = orders.filter(status=self.cleaned_data['status'])
        if self.cleaned_data['created_at']:
            orders = orders.filter(
                created_at__date=self.cleaned_data['created_at'])
        if self.cleaned_data['expired_at']:
            orders = orders.filter(
                expired_at__date=self.cleaned_data['expired_at'])
        return orders


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['product', 'star', 'content', 'image']

    image = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': False}),
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['star'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter product name'}),
            'image': ImagePreviewWidget(
                attrs={
                    'class': 'form-control-file'}),
            'category': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter product price'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter product description'}),
            'average_rating': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.1',
                    'placeholder': 'Enter average rating'}),
            'sold_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter sold quantity'}),
            'is_deleted': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories with is_deleted=False
        self.fields['category'].queryset = Category.objects.filter(
            is_deleted=False)


class ProductDetailForm(forms.ModelForm):
    class Meta:
        model = ProductDetail
        fields = '__all__'
        widgets = {
            'image': ImagePreviewWidget(
                attrs={
                    'class': 'form-control-file'}),
            'size': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter price'}),
            'remain_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter remaining quantity'}),
            'is_deleted': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories with is_deleted=False
        self.fields['product'].queryset = Product.objects.filter(
            is_deleted=False)


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = '__all__'
        widgets = {
            'user': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter address'}),
            'phone_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number'}),
            'voucher': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'status': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'note_content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter any notes (optional)'}),
            'total': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter total amount'}),
            'payment_method': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'expired_at': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Select expiration date'}),
            'is_deleted': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories with is_deleted=False
        self.fields['voucher'].queryset = Voucher.objects.filter(
            is_deleted=False)


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'gender',
            'avatar',
            'default_address',
            'default_phone_number',
            'is_banned'
        ]
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email'}),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter last name'}),
            'gender': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'avatar': forms.FileInput(
                attrs={
                    'class': 'form-control-file'}),
            'default_address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter default address'}),
            'default_phone_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter default phone number'}),
            'is_banned': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
        }


class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = '__all__'
        widgets = {
            'discount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Enter discount percentage'}),
            'started_at': DateTimePickerWidget(
                attrs={
                    'class': 'form-control'}),
            'ended_at': DateTimePickerWidget(
                attrs={
                    'class': 'form-control'}),
            'category': forms.SelectMultiple(
                attrs={
                    'class': 'form-control'}),
            'min_amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter minimum amount'}),
            'is_global': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
            'user': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'is_deleted': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories with is_deleted=False
        self.fields['category'].queryset = Category.objects.filter(
            is_deleted=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name',
                  'default_address', 'default_phone_number']

    def clean_phone_num(self):
        phone_num = self.cleaned_data.get('default_phone_number')
        phone_pattern = re.compile(REGEX_PHONENUM)
        if not phone_pattern.match(phone_num):
            raise forms.ValidationError(
                _("Phone number must be 10 digits and start with 0."))

        return phone_num


class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']

    def clean_avatar(self):
        image = self.cleaned_data.get('avatar')
        if not image and self.instance.avatar:
            raise forms.ValidationError('No image file selected.')
        return image


class PasswordCheckForm(forms.Form):
    current_password = forms.CharField(
        label=_('Current Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        min_length=8,
        help_text=_('Password must be at least 8 characters long.')
    )
    confirm_password = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    _("Passwords do not match!")
                )
        return cleaned_data


class VoucherHistoryForm(forms.ModelForm):
    class Meta:
        model = VoucherHistory
        fields = '__all__'
        widgets = {
            'user': forms.Select(
                attrs={
                    'class': 'form-control'}),
            'voucher': forms.Select(
                attrs={
                    'class': 'form-control'})
        }
