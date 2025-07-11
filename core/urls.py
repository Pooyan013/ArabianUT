from django.urls import path
from .views import index, car_management_view, job_detail_view, edit_car_view, update_job_status_view

app_name = "core"

urlpatterns = [
    path("", index, name="home",),
    path('cars/', car_management_view, name='car_list'),
    path('job/<int:job_id>/', job_detail_view, name='job_detail'),
    path('car/<int:car_id>/edit/', edit_car_view, name='edit_car'),
    path('job/<int:job_id>/update_status/<str:next_status>/', update_job_status_view, name='update_job_status'),

]
