from django import forms
from .models import Income, Expense, Attendance, ExpenseCategory, SalarySlip, Employee
from django.contrib.auth.models import User
from core.models import  Car, Part
from django.db.models import Q
from accounting.models import Employee
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['repair_job', 'source', 'description', 'amount']
        widgets = {
            'repair_job': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
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
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('full_name'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'reason']
        labels = {
            'employee': 'Employee',
            'date': 'Date of Absence',
            'reason': 'Reason (Optional)',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sick Leave'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].required = False

class ExpenseTypeForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select'})
        }

class BuyPartForm(forms.Form):
    car = forms.ModelChoiceField(
        queryset=Car.objects.filter(jobs__status__in=[
            'pending_expert', 'quotation', 'pending_approval', 'pending_start', 'pending_part',
            'working', 'ready_exit', 'sign', 'exit', 'paid'
        ]).distinct(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select Car'
        }),
        label="Car"
    )
    part = forms.ModelChoiceField(
        queryset=Part.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Select Part'
        }),
        label="Part"
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Price'
        }),
        label="Price"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'car' in self.data:
            try:
                car_id = int(self.data.get('car'))
                self.fields['part'].queryset = Part.objects.filter(
                    repair_job__car_id=car_id,
                    is_bought=False
                )
            except (ValueError, TypeError):
                pass
        else:
            self.fields['part'].queryset = Part.objects.none()



class SimpleExpenseForm(forms.Form):
    EXPENSE_TYPE_CHOICES = [
        ('', '---------'),
        ('garage', 'Garage'),
        ('personal', 'Personal'),
        ('other', 'Other'),
    ]
    
    expense_type = forms.ChoiceField(
        choices=EXPENSE_TYPE_CHOICES,
        label="Expense Type"
    )
    
    category = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.all(), 
        required=False, 
        label="Garage Category"
    )
    
    description = forms.CharField(
        max_length=200, 
        required=False, 
        label="Description"
    )
    
    amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        label="Amount"
    )
    
    payment_source = forms.ChoiceField(
        choices=Expense.PaymentSource.choices,
        widget=forms.RadioSelect,
        initial='garage',
        label="Paid From"
    )
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all().order_by('full_name'), 
        required=False,
        label="Employee"
    )
    
    recorded_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        label="Recorded By"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select) or isinstance(field.widget, forms.ModelChoiceField):
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})

        if self.user:
            if not self.user.has_perm('accounting.can_change_expense_recorder'):
                self.fields['recorded_by'].disabled = True
                self.fields['recorded_by'].initial = self.user
            else:
                self.fields['recorded_by'].initial = self.user
                
    def clean(self):
        cleaned_data = super().clean()
        expense_type = cleaned_data.get('expense_type')
        payment_source = cleaned_data.get('payment_source')

        if expense_type == 'garage' and not cleaned_data.get('category'):
            self.add_error('category', 'Please select a category for this expense.')
        
        if expense_type in ['personal', 'other'] and not cleaned_data.get('description'):
            self.add_error('description', 'Description is required for this expense type.')

        if payment_source == 'personal' and not cleaned_data.get('employee'):
            self.add_error('employee', 'Please select the employee who paid from their pocket.')
            
        return cleaned_data


class SalaryAdjustmentForm(forms.Form):
    """Form to add new values to an existing salary slip."""
    paid_add = forms.DecimalField(label="Add to Paid Amount", required=False, max_digits=10, decimal_places=2)
    extra_h_add = forms.FloatField(label="Add Extra Hours", required=False)
    mines_h_add = forms.FloatField(label="Add Minus Hours", required=False)
    extra_add = forms.DecimalField(label="Add Extra Amount (Bonus)", required=False, max_digits=10, decimal_places=2)
    mines_add = forms.DecimalField(label="Add Minus Amount (Deduction)", required=False, max_digits=10, decimal_places=2)
    description = forms.CharField(label="Reason / Description", required=True, widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control mb-2', 'placeholder': '0.00'})

class CloseSlipForm(forms.Form):
    """A simple form to confirm closing a salary slip."""
    confirm_close = forms.BooleanField(label="Yes, I confirm to close this period.", required=True)