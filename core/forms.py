from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import ContactMessage, Product, User, ClothingItem, Employee, CustomerProfile


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
            'ingredients', 'key_benefits', 'directions_for_use', 'price', 'image', 'is_active'
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

class ClothingItemForm(forms.ModelForm):
    class Meta:
        model = ClothingItem
        fields = ['name', 'category', 'price', 'fabric', 'colors', 'sizes', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
                'step': '0.01'
            }),
            'fabric': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown'
            }),
            'colors': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
                'placeholder': 'e.g. White, Beige, Green'
            }),
            'sizes': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-cream border border-organicBrown/30 rounded-lg focus:outline-none focus:border-herbalGreen focus:ring-1 focus:ring-herbalGreen text-organicBrown',
                'placeholder': 'e.g. S, M, L, XL'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-organicBrown file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-lightBeige file:text-herbalGreen hover:file:bg-herbalGreen hover:file:text-cream'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-herbalGreen border-organicBrown/30 rounded focus:ring-herbalGreen'
            }),
        }

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
