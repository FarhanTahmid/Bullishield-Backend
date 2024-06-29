from django.urls import path
from .views import *


app_name='user'

urlpatterns = [
    path('signup/',UserSignup.as_view(),name='signup'),
    path('login/',UserLogin.as_view(),name='login'),
    path('check_authentication/',check_auth_status,name="check_auth"),
    path('user_info/',get_user_info,name='user_info'),
    path('user_profile_update/',update_user_profile,name="update_user_profile"),
    path('upload_profile_picture/',upload_profile_picture,name="upload_profile_picture"),
    
]
