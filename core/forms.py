from django import forms
from .models import Car, RepairJob, QuotationItem, Part

class CarRegistrationForm(forms.ModelForm):
    """Form for registering a new car."""
    class Meta:
        model = Car
        fields = [
            'brand', 'model', 'plate_number', 'color', 'year', 
            'claim_number', 'estimated_cost', 'car_picture',
        ]
        labels = {
            'brand': 'Brand', 'model': 'Model', 'plate_number': 'Plate Number',
            'color': 'Color', 'year': 'Year Manufactured', 'claim_number': 'Claim Number',
            'estimated_cost': 'Estimated Cost Level', 'car_picture': 'Car Picture',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.update({'class': widget_class})

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
    car_brand = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CarBrand'})
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
