from django.contrib import admin
from .models import Expense, Income

admin.site.register(Income)
admin.site.register(Expense)

