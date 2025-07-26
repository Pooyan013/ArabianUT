# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fields = ('name', 'last_name', 'phone_number')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.register(User, UserAdmin)