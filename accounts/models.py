from django.db import models
from django.contrib.auth import admin
from django.contrib.auth.models import User


from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    class Role(models.TextChoices):
        SPECIALIST = 'SP', "Specialist"
        MANAGER = 'MN', "Manager"
        ACCOUNTANT = 'AC', "Accountant"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.SPECIALIST,
        verbose_name="Role"
    )

    def __str__(self):
        return self.user.username
