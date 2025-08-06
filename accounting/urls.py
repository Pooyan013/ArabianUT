from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.accounting_dashboard_view, name='dashboard'),
    path('ajax/get_parts/', views.get_parts_for_car, name='ajax_get_parts'),       
    path('export-excel/', views.export_excel_view, name='export_excel'),
]
