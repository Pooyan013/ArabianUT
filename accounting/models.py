from django.db import models
from django.conf import settings
from core.models import RepairJob 

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

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

class Expense(models.Model):
    """A single model to track all types of expenses."""
    class ExpenseType(models.TextChoices):
        GARAGE = 'garage', "Garage Expense"
        PERSONAL = 'personal', "Personal Expense"
    
    class PersonalType(models.TextChoices):
        ADVANCE = 'advance', "Advance (Employee Debt)"
        REIMBURSEMENT = 'reimbursement', "Reimbursement (Employee Credit)"

    expense_type = models.CharField(
        max_length=10, 
        choices=ExpenseType.choices, 
        verbose_name="Type of Expense"
    )
    description = models.TextField(verbose_name="Description")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    transaction_date = models.DateTimeField(verbose_name="Date and Time of Transaction")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Recorded By")

    category = models.ForeignKey(
        ExpenseCategory, 
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

    person_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Person's Name")
    personal_type = models.CharField(max_length=15, choices=PersonalType.choices, null=True, blank=True, verbose_name="Type of Personal Transaction")

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Expense of {self.amount} for {self.description}"