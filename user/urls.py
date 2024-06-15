from django.urls import path
from .views import *


app_name='user'

urlpatterns = [
    path('signup/',UserSignup.as_view(),name='signup'),
    path('login/',UserLogin.as_view(),name='login'),
    path('check_authentication/',check_auth_status,name="check_auth")
]
