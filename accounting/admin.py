from django.contrib import admin
from .models import Employee, SalarySlip, Attendance, Expense, ExpenseCategory

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'reason') 
    list_filter = ('date', 'employee')            
    search_fields = ('employee__full_name', 'reason') 


admin.site.register(ExpenseCategory)
admin.site.register(Employee)
admin.site.register(SalarySlip)
admin.site.register(Attendance, AttendanceAdmin) 