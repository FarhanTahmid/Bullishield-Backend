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

@admin.register(ScheduledMeetings)
class ScheduledMeetings(admin.ModelAdmin):
    list_display = ['pk', 'user_id' ,'complain_id', 'meeting_time', 'meeting_message']