from django.urls import path
from system import views
app_name='system'


urlpatterns = [
    path('',views.systemOperations,name="operations")
]
