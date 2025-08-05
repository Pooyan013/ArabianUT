from django.db import models
from django.conf import settings
from core.models import RepairJob 
from django.utils import timezone
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")

    def __str__(self):
        return self.name

class Income(models.Model):
    """Tracks all incoming money."""
    repair_job = models.ForeignKey(
        RepairJob, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Related Repair Job"
    )
    source = models.CharField(max_length=200, verbose_name="Source of Income (Payer)")
    description = models.TextField(verbose_name="Description")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    transaction_date = models.DateTimeField(verbose_name="Date and Time of Transaction")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Recorded By")

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Income of {self.amount} from {self.source}"


from django.db import models
from django.conf import settings
from decimal import Decimal

class Employee(models.Model):
    """Stores information about an employee."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        help_text="Link to Django user if the employee can log in."
    )
    full_name = models.CharField(max_length=200)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    id_card = models.CharField(max_length=20, verbose_name="ID Card", default="-")
    card_number = models.CharField(max_length=20, verbose_name="Card Number", default="-")


    def __str__(self):
        return self.full_name
    
class Attendance(models.Model):
    """Logs a single record for each day an employee is absent."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="absences")
    date = models.DateField(verbose_name="Date of Absence")
    reason = models.CharField(max_length=255, blank=True, null=True, verbose_name="Reason for Absence")

    class Meta:
        # Ensures an employee can only have one absence record per day
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"Absence for {self.employee.full_name} on {self.date}"
    
class SalarySlip(models.Model):
    """Stores a single salary payment record for an employee for a specific period."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_slips")
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    
    remaining_before = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    extra_h = models.FloatField(default=0.0) 
    mines_h = models.FloatField(default=0.0) 
    extra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    mines = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    description = models.CharField(max_length=255, blank=True, null=True)

    @property
    def cost(self):
        """
        مبلغ قابل پرداخت را بدون کسر خودکار غیبت محاسبه می‌کند.
        """
        salary = self.employee.base_salary
        
        hour_rate = salary / Decimal('300.0')
        extra_h_cost = Decimal(str(self.extra_h)) * hour_rate
        mines_h_cost = Decimal(str(self.mines_h)) * hour_rate
        
        total_cost = (salary + self.remaining_before - self.paid + 
                      extra_h_cost - mines_h_cost + 
                      self.extra - self.mines)
        
        return round(total_cost, 2)
      
    @property
    def rest(self):
        """Calculates the REMAINING balance for the next period."""
        # This seems to be the total owed before this period's payment
        total_owed = self.employee.base_salary + self.remaining_before + self.extra - self.mines
        remaining = total_owed - self.paid
        return round(remaining, 2)

    def __str__(self):
        return f"Salary for {self.employee.full_name} for period ending {self.pay_period_end}"
    


from django.db import models
from django.conf import settings

class Expense(models.Model):
    """A unified model to track all types of expenses."""
    class ExpenseType(models.TextChoices):
        GARAGE = 'garage', "Garage Expense"
        PERSONAL = 'personal', "Personal Expense"
        PART = 'part', "Car Part"
        OTHER = 'other', "Other"
    
    class PersonalType(models.TextChoices):
        ADVANCE = 'advance', "Advance (Employee Debt)"
        REIMBURSEMENT = 'reimbursement', "Reimbursement (Employee Credit)"

    # --- Common Fields ---
    expense_type = models.CharField(max_length=10, choices=ExpenseType.choices, verbose_name="Type of Expense")
    description = models.TextField(verbose_name="Description")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    transaction_date = models.DateTimeField(verbose_name="Transaction Date", default=timezone.now)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Recorded By")
    related_part = models.ForeignKey(
        'core.Part',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Related Part (if any)"
    )

    # --- Fields for Garage Expenses ---
    category = models.ForeignKey(
        'ExpenseCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Expense Category"
    )
    custom_category = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Custom Category (Other)"
    )

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Employee"
    )
    personal_type = models.CharField(
        max_length=15, 
        choices=PersonalType.choices, 
        null=True, 
        blank=True, 
        verbose_name="Type of Personal Transaction"
    )

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Expense of {self.amount} for {self.description}"