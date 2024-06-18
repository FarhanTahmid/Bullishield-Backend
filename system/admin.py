from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Complain_types)
class ComplainTypes(admin.ModelAdmin):
    list_display = ['pk', 'complain_type']

@admin.register(UserComplains)
class UserComplains(admin.ModelAdmin):
    list_display=[
        'complainer','organization_id','bully_name','incident_date',
        'complain_status','guilty'
    ]