from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import forms

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',authentication_form=forms.CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register_specialist, name='register'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

]