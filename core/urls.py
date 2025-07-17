from django.urls import path
from .views import (
    index, 
    car_management_view, 
    job_detail_view, 
    edit_car_view, 
    update_job_status_view, 
    generate_quotation_pdf,
    delete_quotation_item_view,
    delete_purchased_part_view
)

app_name = "core"

urlpatterns = [
    # General Pages
    path("", index, name="home"),
    path('cars/', car_management_view, name='car_list'),
    
    # Job and Car Specific Views
    path('job/<int:job_id>/', job_detail_view, name='job_detail'),
    path('car/<int:car_id>/edit/', edit_car_view, name='edit_car'),
    
    # Workflow and Action URLs
    path('job/<int:job_id>/update_status/<str:next_status>/', update_job_status_view, name='update_job_status'),
    path('job/<int:job_id>/quotation/pdf/', generate_quotation_pdf, name='quotation_pdf'),
    
    # --- Corrected URLs for Deleting Items ---
    path('quotation_item/<int:item_id>/delete/', delete_quotation_item_view, name='delete_quotation_item'),
    path('purchased_part/<int:part_id>/delete/', delete_purchased_part_view, name='delete_purchased_part'),
]