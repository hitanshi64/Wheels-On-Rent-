from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, ContactMessage, Profile


class CustomUserCreationForm(UserCreationForm):
    """
    Registration form: username, email, phone number, password, confirm password.
    (password1 / password2 are provided automatically by UserCreationForm.)
    """
    email = forms.EmailField(required=True, help_text="We'll send booking confirmations here.")
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text="10-digit mobile number."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])
        return user


class BookingDetailsForm(forms.ModelForm):
    """
    Collected on the vehicle detail page BEFORE a booking is created:
    name, phone number, address, license ID proof, email, gender.
    """
    class Meta:
        model = Booking
        fields = [
            'renter_name', 'renter_phone', 'renter_email',
            'renter_address', 'renter_gender', 'license_number', 'license_document',
        ]
        widgets = {
            'renter_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'renter_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile number'}),
            'renter_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'renter_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full address'}),
            'renter_gender': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driving licence number'}),
            'license_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'renter_name': 'Full Name',
            'renter_phone': 'Phone Number',
            'renter_email': 'Email Address',
            'renter_address': 'Address',
            'renter_gender': 'Gender',
            'license_number': 'Driving Licence Number',
            'license_document': 'Licence ID Proof (upload photo/PDF)',
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your message'}),
        }
