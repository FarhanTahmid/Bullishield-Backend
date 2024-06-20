from rest_framework import serializers
from .models import *

class UserComplainSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserComplains
        fields = ['bully_name', 'complain_description', 'incident_date', 'complain_status']