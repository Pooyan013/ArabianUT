from django.urls import path
from .views import (
    index, 
    car_management_view, 
    job_detail_view, 
    edit_car_view, 
    update_job_status_view, 
    generate_quotation_pdf,
    delete_part_view,
    mark_part_as_bought_view,
    delete_quotation_item_view,
    resume_timer_view,
    pause_timer_view,
    generate_car_owner_pdf
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
    path('part/<int:part_id>/mark_as_bought/', mark_part_as_bought_view, name='mark_part_as_bought'),

    # --- Corrected URLs for Deleting Items ---
    path("part/delete/<int:part_id>/", delete_part_view, name="delete_part"),
    path('quotation_item/<int:item_id>/delete/', delete_quotation_item_view, name='delete_quotation_item'),

    path('job/<int:job_id>/pause/', pause_timer_view, name='pause_timer'),
    path('job/<int:job_id>/resume/', resume_timer_view, name='resume_timer'),
    path('car/<int:car_id>/pdf/', generate_car_owner_pdf, name='car_owner_pdf'),
        

]