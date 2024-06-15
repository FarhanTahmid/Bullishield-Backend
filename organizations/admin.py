from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(OrganizationTypes)
class OrganizationType(admin.ModelAdmin):
    list_display=[
        'pk','type'
    ]

@admin.register(OrganizationData)
class OrganizationData(admin.ModelAdmin):
    list_display=[
        'pk','name','type'
    ]
