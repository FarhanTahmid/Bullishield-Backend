from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from user.models import *



# Create your views here.
class UserSignup(APIView):
    
    def post(self,request):
        # get json data
        data = request.data
        # get username password and email from json data
        username = data.get('username')
        email = data.get('email')
        
        password = data.get('password')

        # Check if the username and email are already taken
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({'error': 'User with username or email already. Try logging in instead.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create a new user if only a member is registered in the organization database
        try:
            UserInformations.objects.get(user_id=username)
            new_user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password)
            )
            new_user.save()
            return Response({'success': f'Signup successful. A new user with {username} was created'}, status=status.HTTP_201_CREATED)

        except UserInformations.DoesNotExist:
            return Response({'error': 'Username Does not exist in the Organisation Database!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserLogin(APIView):
    
    def post(self,request):
        # get data from the request
        data=request.data
        
        # get username and password
        username=data.get('username')
        password=data.get('password')

        user=authenticate(username=username,password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'msg':"Login Successful",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid credentials. Try again!'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth_status(request):
    return Response({'msg': 'Authenticated'},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        username = request.user.username
        # get user info from database
        user_info = UserInformations.objects.get(user_id=username)
        
        return Response({
            'msg':'Got user information',
            'user_info':{
                'user_id':user_info.user_id,
                'organization':user_info.organization_id.name,
                'full_name':user_info.full_name,
                'user_picture':'/media_files/'+str(user_info.user_picture),
                'birth_date':user_info.birth_date,
                'contact_no':user_info.contact_no,
                'email_address':user_info.email_address,
                'home_address':user_info.home_address,
                'gender':user_info.gender,
            }
        },status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        username=request.user.username
        # get user object form UserInformations
        try:
            user=UserInformations.objects.get(user_id=username)
            # get data from the request
            data=request.data
            # update user information
            user.full_name=data.get('full_name')
            user.contact_no=data.get('contact_no')
            user.email_address=data.get('email_address')
            user.home_address=data.get('home_address')
            user.save()
            return Response({'msg':"Profile Information was update"},status=status.HTTP_200_OK)
        except UserInformations.DoesNotExist:
            return Response({'msg': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)