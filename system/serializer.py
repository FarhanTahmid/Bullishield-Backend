from rest_framework import serializers
from .models import *

class UserComplainSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserComplains
        fields = ['complainer','organization_id','complain_type',
            'bully_name','bully_id',
            'incident_date','complain_description','complain_validation',
            'complain_status','proctor_decision','guilty'
        ]