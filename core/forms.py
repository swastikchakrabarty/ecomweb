from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import ContactMessage, Product, User, Employee, CustomerProfile, ProductReview, Address



class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['profile_image', 'default_address']
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-xs text-organicBrown/70 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-lightBeige file:text-herbalGreen hover:file:bg-herbalGreen hover:file:text-cream cursor-pointer',
                'accept': 'image/*',
            }),
            'default_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/15 rounded-xl text-sm focus:outline-none focus:border-herbalGreen text-darkGreen font-medium transition-colors h-28 resize-none',
                'placeholder': 'e.g. 45, Ground Floor, Near Shiv Temple, Udaipurwati, Rajasthan - 333307',
                'rows': 4,
            }),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown placeholder-organicBrown/50 transition-all',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown placeholder-organicBrown/50 transition-all',
                'placeholder': 'Your Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown placeholder-organicBrown/50 transition-all',
                'placeholder': 'Your Contact Number'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown placeholder-organicBrown/50 transition-all h-32 resize-none',
                'placeholder': 'Tell us what health goals or products you are interested in...'
            }),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'subtitle_tagline', 'description', 'total_quantity_info',
            'ingredients', 'key_benefits', 'directions_for_use', 'price',
            'image', 'image_2', 'image_3', 'stock', 'is_active',
            'is_best_seller', 'is_new_arrival', 'is_trending',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'subtitle_tagline': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown h-24'
            }),
            'total_quantity_info': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown h-20',
                'placeholder': 'Comma-separated ingredients'
            }),
            'key_benefits': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown h-20',
                'placeholder': 'One benefit per line'
            }),
            'directions_for_use': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown h-20'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
                'step': '0.01'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-organicBrown file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-lightBeige file:text-herbalGreen hover:file:bg-herbalGreen hover:file:text-cream'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'
            }),
            'image_2': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-organicBrown file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-lightBeige file:text-herbalGreen hover:file:bg-herbalGreen hover:file:text-cream'
            }),
            'image_3': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-organicBrown file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-lightBeige file:text-herbalGreen hover:file:bg-herbalGreen hover:file:text-cream'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
                'min': '0'
            }),
            'is_best_seller': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'}),
            'is_new_arrival': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Password'
    }))

class EmployeeCreationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Username'
    }))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Password'
    }))
    employee_id = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Employee ID'
    }))
    designation = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
        'placeholder': 'Designation'
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Employee.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("An employee with this Employee ID already exists.")
        return employee_id


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['user_name', 'rating', 'comment']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/20 rounded-lg focus:outline-none focus:border-herbalGreen text-darkGreen text-sm',
                'placeholder': 'Your name'
            }),
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
                attrs={
                    'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/20 rounded-lg focus:outline-none focus:border-herbalGreen text-darkGreen text-sm'
                }
            ),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-cream border border-organicBrown/20 rounded-lg focus:outline-none focus:border-herbalGreen text-darkGreen text-sm h-28 resize-none',
                'placeholder': 'Share your experience with this product...'
            }),
        }


class AddressForm(forms.ModelForm):
    """Form for customer saved address management."""
    class Meta:
        model = Address
        fields = ['label', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'phone_number', 'is_default']

    _cls = 'w-full px-4 py-3 bg-cream border border-organicBrown/15 rounded-xl text-sm focus:outline-none focus:border-herbalGreen text-darkGreen font-medium transition-colors'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'label': 'e.g. Home, Work, Other',
            'address_line_1': 'House No., Street Name',
            'address_line_2': 'Landmark, Area (optional)',
            'city': 'City',
            'state': 'State',
            'postal_code': '6-digit PIN Code',
            'phone_number': '10-digit contact number',
        }
        for field_name, field in self.fields.items():
            if field_name == 'is_default':
                field.widget.attrs['class'] = 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'
            else:
                field.widget.attrs['class'] = self._cls
                if field_name in placeholders:
                    field.widget.attrs['placeholder'] = placeholders[field_name]
