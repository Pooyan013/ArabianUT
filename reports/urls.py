from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('operational/', views.operational_report_view, name='operational_report'),
    path('financial/', views.financial_report_view, name='financial_report'),
    path('operational/export/excel/', views.export_operational_report_excel, name='export_operational_excel'),
    path('financial/export/excel/', views.export_financial_report_excel, name='export_financial_excel'),
    path('payroll/', views.payroll_report_view, name='payroll_report'),
]