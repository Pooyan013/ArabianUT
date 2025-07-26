from django.db import models
from django.contrib.auth import admin
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    phone_number = models.CharField(max_length=15, verbose_name="Phone Number")
    name = models.CharField(max_length=60, verbose_name="FirstName", default="Name")
    last_name = models.CharField(max_length=60, verbose_name="LastName", default="LastName")
    def __str__(self):
        return self.user.username
