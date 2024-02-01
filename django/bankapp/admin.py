from django.contrib import admin

# Register your models here.

from .models import User, Transfer

admin.site.register(User)
admin.site.register(Transfer)
