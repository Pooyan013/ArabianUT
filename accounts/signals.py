# accounts/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    فقط زمانی که یک کاربر جدید ساخته می‌شود، اگر پروفایلی وجود نداشت، برای او پروفایل ایجاد می‌کند.
    """
    if created and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()