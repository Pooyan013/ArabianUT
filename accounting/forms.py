from django import forms
from .models import Income, Expense, ExpenseCategory, Attendance

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
            'category', 'custom_category', 
            'employee', 'personal_type',
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


from django import forms
from .models import SalarySlip

class SalarySlipForm(forms.ModelForm):
    class Meta:
        model = SalarySlip
        fields = [
            'employee', 'pay_period_start', 'pay_period_end', 'paid',
            'extra_h', 'mines_h', 'extra', 'mines', 'description'
        ]
        widgets = {
            'pay_period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pay_period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes
        for field_name, field in self.fields.items():
            if 'date' not in field_name:
                field.widget.attrs.update({'class': 'form-control'})

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'reason']
        labels = {
            'employee': 'Employee',
            'date': 'Date of Absence',
            'reason': 'Reason (Optional)',
        }
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }
