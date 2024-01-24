from django.contrib import admin

# Register your models here.

from .models import UserProfile, Transfer

admin.site.register(UserProfile)

admin.site.register(Transfer)