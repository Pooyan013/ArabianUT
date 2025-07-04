from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SpecialistRegistrationForm
from .models import UserProfile

def register_specialist(request):
    if request.method == 'POST':
        form = SpecialistRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            phone_number = form.cleaned_data.get('phone_number')

            new_user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            UserProfile.objects.create(
                user=new_user,
                phone_number=phone_number
            )

            login(request, new_user)
            
            return redirect('core:home')  
    else:
        form = SpecialistRegistrationForm()
        
    return render(request, 'accounts/signup.html', {'form': form})
