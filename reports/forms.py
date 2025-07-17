from django import forms

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )