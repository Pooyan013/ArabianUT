from django import forms
from .models import Car, RepairJob, QuotationItem, Part, Owner
from markdownx.widgets import MarkdownxWidget
from markdownx.models import MarkdownxField
class CarRegistrationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'image', 'plate_number', 'color', 'year', 
            'claim_number', 'estimated_cost', 'vin_number' 
        ]
        labels = {
            'brand': 'Brand',
            'model': 'Model',
            'image': 'Car Image',
            'plate_number': 'Plate Number',
            'color': 'Color',
            'year': 'Year Manufactured',
            'claim_number': 'Claim Number',
            'estimated_cost': 'Estimated Cost Level',
            'vin_number': "VIN Number"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

                
class OwnerForm(forms.ModelForm):
    """Form for creating a new car owner."""
    class Meta:
        model = Owner
        fields = ['name', 'phone_number']
        labels = {
            'name': 'Full Name',
            'phone_number': 'Phone Number',
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
    class Meta:
        model = QuotationItem
        fields = ['item_name', 'custom_name', 'quantity', 'price', 'position']
        labels = {
            'item_name': 'Item (select from list)',
            'custom_name': 'Custom Item Name (if not in list)',
            'quantity': 'Quantity',
            'price': 'Unit Price',
            'position': 'Position',
        }
        widgets = {
            'custom_name': forms.TextInput(attrs={'class': 'form-control'}),
            'item_name': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'price': forms.NumberInput(attrs={'step': 0.01}),
            'position': forms.Select(),
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
        fields = ['name', 'picture', ]
        labels = {
            'name': 'Item/Part Name',
            'picture': 'Picture (Optional)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
class BuyPartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }