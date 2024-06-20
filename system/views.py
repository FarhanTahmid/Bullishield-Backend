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
from .complain_handler import ComplainHandler
from .serializer import *

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getUserComplains(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        data=request.data
        # get the complainer
        user_id=data.get('user_id')
        # get user object
        try:
            user=UserInformations.objects.get(user_id=user_id)
        except UserInformations.DoesNotExist:
            return Response({'msg':"Session timed out. Please login again!"},status=status.HTTP_400_BAD_REQUEST)
        
        complaints = UserComplains.objects.filter(complainer=user)
        serializer=UserComplainSerializer(complaints,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

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
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
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
        harassment_type=data.get('harassment_type')
        # get harassment type object
        complain_type=Complain_types.objects.filter(complain_type=harassment_type).first()
        complain_type_id=complain_type.pk
        # create a complain first
        create_complain,complain_pk=ComplainHandler.createComplains(
            complainer_id=complainer_id,complain_type_id=complain_type_id,
            bully_name=bully_name,bully_id=bully_id,incident_date=incident_date,
            complain_description=complain_description
        )
        if(create_complain):
            # get evidence files
            try:
                for file in request.FILES.getlist('image_proves'):
                    new_proof=UserComplainProof.objects.create(
                        complain_id=UserComplains.objects.get(pk=complain_pk),proof=file
                    )
                    new_proof.save()
            except Exception as e:
                print(e)
                return Response({'msg': "Complain registered! Could not upload Proves"},status=status.HTTP_424_FAILED_DEPENDENCY)

            # get bully pictures
            try:
                for file in request.FILES.getlist('bully_image'):
                    new_bully_image=BullyPictures.objects.create(
                        complain_id=UserComplains.objects.get(pk=complain_pk),bully_image=file
                    )
                    new_bully_image.save()
            except Exception as e:
                print(e)
                return Response({'msg': "Complain registered! Could not upload Bully Pictures"},status=status.HTTP_424_FAILED_DEPENDENCY)

            return Response({'msg': "Complain Registered! We will get back to you soon!"},status=status.HTTP_200_OK)
        else:
            return Response({'msg': "Complain can not be registered!"},status=status.HTTP_403_FORBIDDEN)