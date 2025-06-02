from django import forms
from .models import User, Book, BookRentRequest

class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'password']

class AdminSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'password']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number']


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'unique_id', 'author', 'cover_photo', 'pdf']

class BookRequestActionForm(forms.ModelForm):
    class Meta:
        model = BookRentRequest
        fields = ['status']