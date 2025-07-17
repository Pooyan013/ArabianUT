from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages



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