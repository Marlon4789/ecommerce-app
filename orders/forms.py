from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['full_name', 'email', 'address', 'postal_code', 'city']
        widgets = {
            'full_name':   forms.TextInput(attrs={
                'class': 'form-control border border-secondary rounded-2',
                'placeholder': 'Nombre completo',
            }),
            'email':       forms.EmailInput(attrs={
                'class': 'form-control border border-secondary rounded-2',
                'placeholder': 'Correo electrónico',
            }),
            'address':     forms.TextInput(attrs={
                'class': 'form-control border border-secondary rounded-2',
                'placeholder': 'Cra 1 # 2-3 descripción corta',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control border border-secondary rounded-2',
                'placeholder': 'Código postal',
            }),
            'city':        forms.TextInput(attrs={
                'class': 'form-control border border-secondary rounded-2',
                'placeholder': 'Ciudad',
            }),
        }