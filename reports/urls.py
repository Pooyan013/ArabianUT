from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('operational/', views.operational_report_view, name='operational_report'),
    path('financial/', views.financial_report_view, name='financial_report'),
    path('operational/export/excel/', views.export_operational_excel, name='export_operational_excel'),
    path('financial/export/excel/', views.export_financial_report_excel, name='export_financial_excel'),
    path('payroll/', views.payroll_report_view, name='payroll_report'),
    path('', views.payroll_dashboard_view, name='payroll_dashboard'),
    path('employee/<int:employee_id>/', views.employee_payroll_detail_view, name='employee_detail'),
    path('slip/<int:slip_id>/adjust/', views.add_salary_adjustment_view, name='add_adjustment'),
    path('slip/<int:slip_id>/close/', views.close_salary_slip_view, name='close_slip'),
    path('profit-report/', views.profit_report_view, name='profit_report'),


]