from django.shortcuts import render,redirect
from .system_functions import SystemOperations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from user.models import UserInformations
from .models import *
# Create your views here.

def systemOperations(request):
    
    print("Choose operations to perform. Enter 0 to exit the program")
    
    while True:
        print("1. Register users from CSV files")
        print("2. Create Organization Types")
        print("3. Create Organizations")
        
        choice=int(input("Your choice: "))
        
        if choice==0:
            break
        elif(choice==1):
            # trigger the register user function
            result=SystemOperations.register_user_with_csv()
            if(result):
                print("User Registration was successful!")
                return redirect('system:operations')
            else:
                print("Something went wrong!")
                return redirect('system:operations')


    return render(request,"index.html")

@api_view(['GET'])
def getComplainTypes(request):
    # get all harassment types
    try:
        complain_type_objects=Complain_types.objects.all().order_by('pk')
        complain_types={}
        for type in complain_type_objects:
            complain_types.update({type.pk:type.complain_type})
        return Response({'types':complain_types},status=status.HTTP_200_OK)
    except Complain_types.DoesNotExist:
        return Response({'error':"Something went wrong while fetching Complain Types!"},status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registerComplain(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        # get data
        data=request.data
        # get the complainer
        complainer_id=data.get('complainer_id')

        # get bully details
        bully_name=data.get('bully_name')
        bully_id=data.get('bully_id')
        
        # get complain details
        incident_date=data.get('incident_date')
        complain_description=data.get('complain_description')
        
        # get harassment type
        harassment_type_id=data.get('harassment_type')

        # get evidence files
        
        print(complainer_id)
        print(bully_name)
        print(bully_id)
        print(incident_date)
        print(complain_description)
        print(harassment_type_id)
        
        return Response({'msg': "Complain Registered!"},status=status.HTTP_200_OK)