import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import RepairJob

@receiver(pre_save, sender=RepairJob)
def delete_images_on_archive(sender, instance, **kwargs):
    """
    Signal to delete car and quotation images when a RepairJob is archived.
    """
    if not instance.pk:
        return

    try:
        old_instance = RepairJob.objects.get(pk=instance.pk)
    except RepairJob.DoesNotExist:
        return

    if old_instance.status != 'archived' and instance.status == 'archived':
        car = instance.car
        
        if car.image:
            if os.path.isfile(car.image.path):
                os.remove(car.image.path)
                print(f"Deleted car picture: {car.image.path}")

        for item in instance.quotation_items.all():
            if item.picture:
                if os.path.isfile(item.picture.path):
                    os.remove(item.picture.path)
                    print(f"Deleted quotation picture: {item.picture.path}")