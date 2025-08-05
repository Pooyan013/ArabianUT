from django.urls import path
from . import views
from .views import get_parts_ajax

app_name = 'accounting'

urlpatterns = [
    path('', views.accounting_dashboard_view, name='dashboard'),
    path('ajax/get_parts/', get_parts_ajax, name='get_parts_ajax'),
]