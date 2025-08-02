from django import forms
from .models import Car, RepairJob, QuotationItem, Part, Owner

class CarRegistrationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'image','plate_number', 'color', 'year', 
            'claim_number', 'estimated_cost',
        ]
        labels = {
            'brand': 'Brand',
            'model': 'Model',
            'plate_number': 'Plate Number',
            'color': 'Color',
            'year': 'Year Manufactured',
            'claim_number': 'Claim Number',
            'estimated_cost': 'Estimated Cost Level',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': widget_class})

class OwnerForm(forms.ModelForm):
    """Form for creating a new car owner."""
    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'phone_number', 'vin_number']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': 'Phone Number',
            'vin_number': 'WIN/VIN Number',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
class DealUpdateForm(forms.ModelForm):
    """Form to update the deal amount for a repair job."""
    class Meta:
        model = RepairJob
        fields = ['deal']
        labels = {'deal': 'Deal Amount from Insurance'}
        widgets = {
            'deal': forms.NumberInput(attrs={'class': 'form-control'})
        }

class QuotationItemForm(forms.ModelForm):
    """Form to add an item to the quotation."""
    class Meta:
        model = QuotationItem
        fields = ['name', 'picture', 'price']
        labels = {
            'name': 'Item/Part Name',
            'picture': 'Picture (Optional)',
            'price': 'Estimated Price',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class LpoConfirmationForm(forms.ModelForm):
    """Form for final LPO  confirmation."""
    class Meta:
        model = RepairJob
        fields = ['lpo_confirmed']
        labels = {
            'lpo_confirmed': 'I confirm the LPO is positive.',
        }
class SignConfirmationForm(forms.ModelForm):
        """Form for  Signature confirmation."""
        class Meta:
            model = RepairJob
            fields = ['sign_confirmed']
            labels = {
                'sign_confirmed': 'I confirm the customer signature is received.',
            }

class JobFilterForm(forms.Form):
    """Form for filtering the list of repair jobs."""
    STATUS_CHOICES = [('', 'All Statuses')] + RepairJob.Stage.choices
    ESTIMATE_CHOICES = [('', 'All Estimates')] + Car.ESTIMATE_COST_CHOICES
    
    plate_number = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plate Number'})
    )
    claim_number = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ClaimNumber'})
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estimated_cost = forms.ChoiceField(
        choices=ESTIMATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class PartItemForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'picture', 'price',]
        labels = {
            'name': 'Item/Part Name',
            'picture': 'Picture (Optional)',
            'price': 'Estimated Price',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
