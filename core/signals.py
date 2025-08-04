import os
from django.db.models.signals import post_save  
from django.dispatch import receiver
from .models import RepairJob

@receiver(post_save, sender=RepairJob)
def delete_images_on_archive(sender, instance, created, **kwargs):
    """
    سیگنال برای حذف تصاویر خودرو و قطعات، زمانی که وضعیت یک کار تعمیراتی به 'archived' تغییر می‌کند.
    این سیگنال بعد از ذخیره شدن موفق در دیتابیس اجرا می‌شود.
    """
    if not created and instance.status == 'archived':
        
        car = instance.car
        if car and car.image:
            if hasattr(car.image, 'path') and os.path.isfile(car.image.path):
                os.remove(car.image.path)
                print(f"Deleted car picture: {car.image.path}")
                car.image = None
                car.save()


        for part in instance.parts.all():
            if part.picture:
                if hasattr(part.picture, 'path') and os.path.isfile(part.picture.path):
                    os.remove(part.picture.path)
                    print(f"Deleted part picture: {part.picture.path}")
