from django.db import models

class Car(models.Model):
    ESTIMATE_LEVEL_CHOICES = [
        ("nodamage", "No Damage"),
        ("cheap", "Cheap"),
        ("lite", "Lite"),
        ("mid", "Mid"),
        ("heavy", "Heavy"),
    ]
    brand = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=20)
    color = models.CharField(max_length=20)
    year = models.IntegerField()
    claim_number = models.CharField(max_length=50)
    registered_at = models.DateTimeField(auto_now_add=True)
    lpo_confirmed = models.BooleanField(default=False)

    estimated_time_cost = models.CharField(
        max_length=10,
        choices=ESTIMATE_LEVEL_CHOICES,
        default="mid"
    )

    def __str__(self):
        return f"{self.brand} - {self.plate_number}"

class CarStage(models.Model):
    STAGE_CHOICES = [
        ("pending_expert", "Pending for Expert"),
        ("pending_approval", "Pending Approval"),
        ("pending_start", "Pending to Start"),
        ("pending_part", "Pending Part"),
        ("working", "Working"),
        ("ready_exit", "Ready for Exit"),
        ("archived", "Archived"),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="stages")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    entered_at = models.DateTimeField(auto_now_add=True)

    deal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    required_parts = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.car} - {self.get_stage_display()}"

