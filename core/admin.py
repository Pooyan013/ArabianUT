from django.contrib import admin
from .models import Car, RepairJob, Part, Owner, QuotationItem

admin.site.register(Car)
admin.site.register(RepairJob)
admin.site.register(Part)
admin.site.register(Owner)
admin.site.register(QuotationItem)




