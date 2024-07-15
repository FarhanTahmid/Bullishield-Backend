from django.urls import path
from system import views
from .views import *
app_name='system'


urlpatterns = [
    path('',views.systemOperations,name="operations"),
    path('register_complain/',views.registerComplain,name='register_complain'),
    path('get_complain_type/',views.getComplainTypes,name='complain_type'),
    path('get_user_complains/',views.getUserComplains,name="get_user_complains"),
    path('get_complain_details/',views.getComplainDetails,name="get_complain_details"),
    path('get_proctor_complains/',views.proctorComplainView,name="get_proctor_complains"),
    path('update_complains/',views.updateComplainDetails,name="update_complain"),
    path('meeting/',ScheduleMeeting.as_view(),name='meeting'),
    path('chatbot/',ChatbotAPI.as_view(),name='chatbot'),
]
