from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounting.models import Employee, SalarySlip 

@receiver(post_save, sender=Employee)
def create_first_salary_slip(sender, instance, created, **kwargs):
    """
    زمانی که یک کارمند جدید ساخته می‌شود، به صورت خودکار اولین فیش حقوقی او را ایجاد می‌کند.
    """
    if created:
        today = timezone.now().date()
        pay_period_start = today.replace(day=1)
        
        next_month = pay_period_start.replace(day=28) + timezone.timedelta(days=4)
        pay_period_end = next_month - timezone.timedelta(days=next_month.day)

        SalarySlip.objects.create(
            employee=instance,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            remaining_before=0 
        )
        print(f"First salary slip created for new employee: {instance.full_name}")