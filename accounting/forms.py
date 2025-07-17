from django import forms
from .models import Income, Expense, ExpenseCategory

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['repair_job', 'source', 'description', 'amount', 'transaction_date']
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'expense_type', 'description', 'amount', 'transaction_date', 
            'category', 'custom_category', 'person_name', 'personal_type'
        ]
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})