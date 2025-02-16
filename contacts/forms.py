from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    # Define the company field as a ChoiceField
    COMPANY_CHOICES = [
        ("", "Select Company"),  # Empty option for no selection
        ("AXA", "AXA"),
        ("MetLife", "MetLife"),
        ("Limitless Care", "Limitless Care"),
        ("Others", "Others"),
    ]
    company = forms.ChoiceField(
        choices=COMPANY_CHOICES,
        required=False,  # Allow empty value if needed
        widget=forms.Select(attrs={'class': 'form-control'})  # Optional: Add styling
    )

    class Meta:
        model = Contact
        fields = ['id', 'name', 'company', 'card1', 'card2', 'phone']
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'card1': forms.TextInput(attrs={'class': 'form-control'}),
            'card2': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }