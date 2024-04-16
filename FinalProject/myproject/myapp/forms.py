from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import PaymentInfo, ShippingAddress
from django.core.validators import RegexValidator



class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()  # Automatically fetches the custom user model
        fields = UserCreationForm.Meta.fields + ('email_address',)# Add custom fields here


class PaymentDetailsForm(forms.ModelForm):
    CARD_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('debit','Debit'),
        ('credit','Credit')
    ]
    card_type = forms.ChoiceField(choices=CARD_CHOICES, label="Card Type")
    card_number = forms.CharField(max_length=16, label="Card Number", validators=[
            RegexValidator(r'^\d{13,16}$', message="Enter a valid 13-16 digit credit card number.")
        ])
    cvv = forms.CharField(max_length=4, label="CVV", validators=[
            RegexValidator(r'^\d{3,4}$', message="Enter a valid 3 or 4 digit CVV.")
        ])
    card_nickname = forms.CharField(max_length=16, label="Nickname")
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, label="Payment Method")


    class Meta:
        model = PaymentInfo
        fields = ['card_type', 'card_number', 'cvv', 'card_nickname', 'payment_method']
        labels = {
            'card_number': 'Card Number',
            'cvv': 'CVV',
            'card_nickname':'Nickname',
            'payment_method':'Payment Method'
        }

class ShippingAddressForm(forms.ModelForm):
    STATE_CHOICES = [
        ('NJ','NJ'),
        ('NY','NY'),
        ('PA','PA')
    ]
    COUNTRY_CHOICES = [
        ('US', 'United States')
    ]

    state = forms.ChoiceField(choices=STATE_CHOICES)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = ShippingAddress
        fields = ['street', 'city', 'state', 'country', 'postal_code','nickname']
        labels = {
            'street': 'Street',
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'postal_code': 'Postal Code',
            'nickname':'Nickname'
        }
