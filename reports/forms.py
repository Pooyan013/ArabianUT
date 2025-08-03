from django import forms
from core.models import RepairJob 

class DateRangeFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + RepairJob.Stage.choices
    CONFIRMATION_CHOICES = [
        ('', 'All'),
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    lpo = forms.ChoiceField(
        choices=CONFIRMATION_CHOICES,
        required=False,
        label="LPO Confirmed",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sign = forms.ChoiceField(
        choices=CONFIRMATION_CHOICES,
        required=False,
        label="Signature Confirmed",
        widget=forms.Select(attrs={'class': 'form-select'})
    )