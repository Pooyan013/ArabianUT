from django.urls import path,reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from . import forms

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',authentication_form=forms.CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', views.edit_profile, name='edit_profile'),
        path(
        'password_change/', 
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/password_change.html',
            success_url=reverse_lazy('accounts:password_change_done'),
            form_class=forms.CustomPasswordChangeForm  

        ), 
        name='password_change'
    ),
    path(
        'password_change/done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/password_change_done.html'
        ), 
        name='password_change_done'
    ),
]