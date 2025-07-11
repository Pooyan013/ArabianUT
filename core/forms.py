from django import forms
from .models import RepairJob, Part, Car

class CarRegistrationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 
            'plate_number', 
            'color', 
            'year', 
            'claim_number', 
            'estimated_cost', 
        ]
        labels = {
            'brand': 'Brand',
            'plate_number': 'Plate Number',
            'color': 'Color',
            'year': 'Year Manufactured',
            'claim_number': 'Claim Number',
            'estimated_cost': 'Estimated Cost Level', 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class DealUpdateForm(forms.ModelForm):
    """Form to update the deal amount."""
    class Meta:
        model = RepairJob
        fields = ['deal']
        labels = {'deal': 'Deal Amount from Insurance'}
        widgets = {
            'deal': forms.NumberInput(attrs={'class': 'form-control'})
        }

class PartForm(forms.ModelForm):
    """Form to add a single required part with its picture."""
    class Meta:
        model = Part
        fields = ['name', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Part Name'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



class LPOConfirmationForm(forms.ModelForm):
    """A simple form to update the LPO status."""
    class Meta:
        model = RepairJob
        fields = ['lpo_confirmed']
        labels = {'lpo_confirmed': 'I confirm the LPO is positive and the payment is settled.'}