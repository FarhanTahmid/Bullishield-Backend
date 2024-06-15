from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User,auth
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
            return Response({'error': 'User with username or email already exists'}, status=status.HTTP_401_UNAUTHORIZED)
        
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
            