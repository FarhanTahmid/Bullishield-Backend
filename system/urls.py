from django.urls import path
from system import views
app_name='system'


urlpatterns = [
    path('',views.systemOperations,name="operations"),
    path('register_complain/',views.registerComplain,name='register_complain'),
    path('get_complain_type/',views.getComplainTypes,name='complain_type'),
    path('get_user_complains/',views.getUserComplains,name="get_user_complains"),
    path('get_complain_details/',views.getComplainDetails,name="get_complain_details"),
    
]
