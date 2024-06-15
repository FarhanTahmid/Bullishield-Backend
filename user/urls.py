from django.urls import path
from .views import *


app_name='user'

urlpatterns = [
    path('signup/',UserSignup.as_view(),name='signup')
]
