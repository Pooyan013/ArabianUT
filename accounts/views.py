from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import SpecialistRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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

@login_required
@transaction.atomic
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile Updated Succesfully!')
            return redirect('accounts:edit_profile') 
        else:
            messages.error(request, "Please fill Correctly")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)