
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify

from .models import Customer


class CustomerRegistrationForm(forms.Form):

    name = forms.CharField(
        max_length=150,
        label="Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def save(self):
        name = self.cleaned_data['name'].strip()

        base_username = slugify(name).replace('-', '') or 'customer'
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            first_name=name,
            password=self.cleaned_data['password']
        )

        Customer.objects.create(user=user)

        return user
