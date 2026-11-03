from django import forms
from django.contrib.auth.forms import UserCreationForm
from Admin.models import User




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Add the email field

    class Meta:
        model = User  # Use your custom User model
        fields = ['username', 'email', 'password1', 'password2']  # Add 'email' to fields
        
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control','style': 'color: white;'}),
            'email': forms.EmailInput(attrs={'class': 'form-control' ,'style': 'color: white;'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control' ,'style': 'color: white;'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control' ,'style': 'color: white;'}),
        }
        
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                if field.widget.__class__.__name__ != 'PasswordInput':  # Set class for all except password
                    field.widget.attrs['class'] = 'form-control'
                else:
                    field.widget.attrs['class'] = 'form-control'  # Ensure class is applied to password fields