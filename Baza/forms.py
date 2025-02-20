from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, CURRENCY_CHOICES, Category

USER_TYPE_CHOICES = (
    ('consumer', 'Consumer'),
    ('vendor', 'Vendor'),
)

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text='Enter your full name'
    )
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        help_text='Required if you are a vendor'
    )
    market = forms.CharField(
        max_length=255,
        required=False,
        help_text='Required if you are a vendor'
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label="I accept the Terms and Conditions"
    )

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'user_type', 'phone_number', 'market', 'password1', 'password2', 'terms_accepted')

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        phone_number = cleaned_data.get('phone_number')
        market = cleaned_data.get('market')
        if user_type == 'vendor':
            if not phone_number:
                self.add_error('phone_number', 'Phone number is required for vendors.')
            if not market:
                self.add_error('market', 'Market is required for vendors.')
        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image', 'currency', 'market', 'door_number', 'description', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product name'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price'}),
            'currency': forms.Select(choices=CURRENCY_CHOICES),
            'market': forms.TextInput(attrs={'placeholder': 'Market'}),
            'door_number': forms.TextInput(attrs={'placeholder': 'Door number'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description'}),
            'category': forms.Select(),  # This is where you define that 'category' should be a select dropdown
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Populate the category dropdown with categories from the database
        self.fields['category'].queryset = Category.objects.all()

    

class RateVendorForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Rating (1-5)"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write your feedback here...'}),
        label="Feedback",
        required=True
    )