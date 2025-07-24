from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class Car(models.Model):
    """Stores permanent information about a physical car."""
    ESTIMATE_COST_CHOICES = [
        ("nodamage", "No Damage"),
        ("cheap", "Cheap"),
        ("lite", "Lite"),
        ("mid", "Mid"),
        ("heavy", "Heavy"),
    ]

    brand = models.CharField(max_length=50, verbose_name="Brand")
    model =models.CharField(max_length=50, verbose_name="Model", default='N/A')
    car_picture = models.ImageField(upload_to='cars/', null=True, blank=True,verbose_name="Car Picture")
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="Plate Number")
    color = models.CharField(max_length=20, verbose_name="Color")
    year = models.IntegerField(verbose_name="Year Manufactured")
    claim_number = models.CharField(max_length=50, verbose_name="Claim Number", default='No Claim')
    registered_at = models.DateTimeField(default=timezone.now, verbose_name="Time Registered")
    registered_by = models.ForeignKey(User,on_delete=models.SET_NULL, null=True,blank=True,verbose_name="Registered By")   
    estimated_cost = models.CharField(
        max_length=10,
        choices=ESTIMATE_COST_CHOICES,
        default="mid",
        verbose_name="Estimated Cost Level"
    )

    def __str__(self):
        return f"{self.brand} - {self.plate_number}"

class RepairJob(models.Model):
    """Tracks a single repair process for a car from start to finish."""
    class Stage(models.TextChoices):
        PENDING_EXPERT = 'pending_expert', "Pending for Expert"
        QUOTATION = 'quotation', "Quotation" 
        PENDING_APPROVAL = 'pending_approval', "Pending Approval"
        PENDING_START = 'pending_start', "Pending to Start"
        PENDING_PART = 'pending_part', "Pending Part"
        WORKING = 'working', "Working"
        READY_TOEXIT = 'ready_exit', "Ready To Exit"
        SIGN = 'sign', "Waiting For Sign" 
        EXIT = 'exit', "Exit (Awaiting LPO)" 
        PAIED = 'paied', "Waiting For Pay"
        ARCHIVED = 'archived', "Archived"

    # --- Core Information ---
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="jobs", verbose_name="Car")
    status = models.CharField(max_length=20, choices=Stage.choices, default=Stage.PENDING_EXPERT, verbose_name="Status")
    
    # --- Stage-Specific Data ---
    deal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Deal Amount")
    
    # --- Timestamps for each stage ---
    expert_inspected_at = models.DateTimeField(null=True, blank=True, verbose_name="Time of Expert Inspection")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Time of Approval")
    work_started_at = models.DateTimeField(null=True, blank=True, verbose_name="Time Work Started")
    parts_pending_at = models.DateTimeField(null=True, blank=True, verbose_name="Time Parts Became Pending")
    work_finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Time Work Finished")
    exited_at = models.DateTimeField(null=True, blank=True, verbose_name="Time of Exit")
    timer_start_time = models.DateTimeField(null=True, blank=True, verbose_name="Timer Start Time")
    timer_end_time = models.DateTimeField(null=True, blank=True, verbose_name="Timer End Time")
    timer_paused_at = models.DateTimeField(null=True, blank=True, verbose_name="Timer Paused At")

    # --- Finalization ---
    lpo_confirmed = models.BooleanField(default=False, verbose_name="LPO Confirmed")
    sign_confirmed = models.BooleanField(default=False, verbose_name="Sign Confirmed")
    
    def __str__(self):
        return f"Job for {self.car} - {self.get_status_display()}"

class Part(models.Model):
    """Represents a single required part with its picture for a repair job."""
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name="parts", verbose_name="Repair Job")
    name = models.CharField(max_length=200, verbose_name="Part Name")
    picture = models.ImageField(upload_to="parts/", verbose_name="Part Picture", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Part Price", default=10.00)
    is_bought = models.BooleanField(default=False, verbose_name="Is Bought?")

    def __str__(self):
        return f"{self.name} for Job #{self.repair_job.id}"

class QuotationItem(models.Model):
    """
    The single, definitive model for an item in a quotation.
    """
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name="quotation_items")
    name = models.CharField(max_length=200, verbose_name="Item Name")
    picture = models.ImageField(upload_to="quotations/", null=True, blank=True, verbose_name="Item Picture")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Estimated Price")

    def __str__(self):
        return f"Quote Item: {self.name} for Job #{self.repair_job.id}"
    
