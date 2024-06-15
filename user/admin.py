from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserInformations)
class RegisteredUsers(admin.ModelAdmin):
    list_display=[
        'user_id','organization_id','full_name','gender','is_proctor'
    ]