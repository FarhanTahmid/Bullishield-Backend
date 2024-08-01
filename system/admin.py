from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Complain_types)
class ComplainTypes(admin.ModelAdmin):
    list_display = ['pk', 'complain_type']

@admin.register(UserComplains)
class UserComplains(admin.ModelAdmin):
    list_display=[
        'pk','complainer','organization_id','bully_name','incident_date',
        'complain_status','guilty'
    ]

@admin.register(UserComplainProof)
class UserComplainProves(admin.ModelAdmin):
    list_display=[
        'pk','complain_id','proof','cyber_bullying_flag'
    ]

@admin.register(ScheduledMeetings)
class ScheduledMeetings(admin.ModelAdmin):
    list_display = ['pk', 'user_id' ,'complain_id', 'meeting_time', 'meeting_message']
    

@admin.register(ChatbotThreads)
class UserChatbotThreads(admin.ModelAdmin):
    list_display=['user_id','thread_id']
    
@admin.register(SchedulerRecords)
class SchedulerRecords(admin.ModelAdmin):
    list_display=['pk','job_id','execution_status']

@admin.register(ComplainProofExtractedStrings)
class ExtractedStrings(admin.ModelAdmin):
    list_display=['pk','image_id','extracted_strings','prediction_confidence','cyberBullyingFlag']