from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField


class Owner(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name", default='Unnamed Owner')
    phone_number = models.CharField(max_length=30, verbose_name="Phone Number")
    class Meta:
        verbose_name = "Owner"
        verbose_name_plural = "Owners"

    def __str__(self):
        return f"{self.name}"
    
class Car(models.Model):
    """Stores permanent information about a physical car."""
    ESTIMATE_COST_CHOICES = [
        ("nodamage", "No Damage"),
        ("cheap", "Cheap"),
        ("lite", "Lite"),
        ("mid", "Mid"),
        ("heavy", "Heavy"),
    ]
    BRAND_CHOICES = [
        ('MERCEDES', 'MERCEDES'),
        ('BMW', 'BMW'),
        ('GMC', 'GMC'),
        ('NISSAN', 'NISSAN'),
        ('HYUNDAI', 'HYUNDAI'),
        ('AUDI', 'AUDI'),
        ('TOYOTA', 'TOYOTA'),
        ('LEXUS', 'LEXUS'),
        ('INFINITY', 'INFINITY'),
        ('DODGE', 'DODGE'),
        ('MAZDA', 'MAZDA'),
        ('HONDA', 'HONDA'),
        ('KIA', 'KIA'),
        ('LAND ROVER', 'LAND ROVER'),
        ('PORSCHE', 'PORSCHE'),
        ('CHEVROLET', 'CHEVROLET'),
        ('FORD', 'FORD'),
        ('PEUGEOT', 'Peugeot'),
        ('JEEP', 'JEEP'),
        ('MITSUBISHI', 'MITSUBISHI'),
        ('SUZUKI', 'SUZUKI'),
        ('V WAGON', 'V WAGON'),
        ('MINI', 'MINI'),
        ('MG', 'MG'),
        ('RENAULT', 'RENUALT'),
        ('GENESIS', 'GENESIS'),
        ('CHANGAN', 'CHANGAN'),
        ('GEELY', 'GEELY'),
        ('SUBARU', 'SUBARU'),
        ('CADILLAC', 'CADILAC'),
        ('JETOUR', 'JETOUR'),
        ('JAGUAR', 'JAGUAR'),
        ('VOLVO', 'VOLVO'),
        ('OTHER', 'Other'),
    ]

    # --- Choices for Color Dropdown ---
    COLOR_CHOICES = [
        ('RED', 'Red'),
        ('WHITE', 'White'),
        ('BLACK', 'Black'),
        ('BLUE', 'Blue'),
        ('SILVER', 'Silver'),
        ('YELLOW', 'Yellow'),
        ('GREEN', 'Green'),
        ('GRAY', 'Gray'),
        ('GOLD', 'Gold'),
        ('BROWN', 'Brown'),
    ]

    brand = models.CharField(max_length=50, verbose_name="Brand", choices=BRAND_CHOICES, default='OTHER')
    model =models.CharField(max_length=50, verbose_name="Model", default='N/A')
    image = models.ImageField(upload_to='car_pictures/', null=True, blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    plate_number = models.CharField(max_length=20, unique=True, verbose_name="Plate Number")
    color = models.CharField(max_length=20, verbose_name="Color", choices=COLOR_CHOICES, default='WHITE')    
    year = models.IntegerField(verbose_name="Year Manufactured")
    claim_number = models.CharField(max_length=50, verbose_name="Claim Number", default='No Claim')
    vin_number = models.CharField(max_length=25, verbose_name="VIN Number", unique=True,null=True, blank=True)

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
    
    @property
    def is_archived(self):
        return not self.jobs.filter(is_archived=False).exists()
    
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
        PAID = 'paid', "Waiting For Pay"
        ARCHIVED = 'archived', "Archived"

    # --- Core Information ---
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="jobs")
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
    class Meta:
        permissions = [
            ("can_manage_repair_dashboard", "Can manage repair dashboard"),
        ]

class Part(models.Model):
    """Represents a single required part with its picture for a repair job."""
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name="parts", verbose_name="Repair Job")
    name = models.CharField(max_length=200, verbose_name="Part Name")
    picture = models.ImageField(upload_to="parts/", verbose_name="Part Picture", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Part Price", default=10.00)
    is_bought = models.BooleanField(default=False, verbose_name="Is Bought?")

    def __str__(self):
        if self.repair_job:
            return f"{self.name} for Job #{self.repair_job.id}"
        else:
            return f"{self.name} (No associated job)"
class ItemName(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class QuotationItem(models.Model):
    POSITION_CHOICES = [
        ('front', 'Front'),
        ('left', 'Left'),
        ('right', 'Right'),
        ('rear', 'Rear'),
        ('front_right', 'Front Right'),
        ('rear_left', 'Rear Left'),
        ('rear_right', 'Rear Right'),
        ('center', 'Center'),
        ('unknown', 'Unknown'),
    ]
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name="quotation_items")
    item_name = models.ForeignKey(ItemName, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Item Name")
    custom_name = models.CharField(max_length=200, blank=True, verbose_name="Custom Item Name (if not in list)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Unit Price")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='unknown', verbose_name="Position")

    @property
    def display_name(self):
        return self.item_name.name if self.item_name else self.custom_name

    @property
    def amount(self):
        return self.quantity * self.price

    def __str__(self):
        return f"Quote Item: {self.display_name} x{self.quantity} for Job #{self.repair_job.id}"
