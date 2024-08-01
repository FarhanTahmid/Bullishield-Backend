from django.shortcuts import render,redirect
from .system_functions import SystemOperations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from pathlib import Path
import regex
from system.chatbot import Chatbot
from user.models import UserInformations
from .models import *
from .complain_handler import ComplainHandler
from .serializer import *
from .model_operations import DataProcessingAndOperations
from apscheduler.schedulers.background import BlockingScheduler

# import easyocr


# Create your views here.

def example_extract_text_from_picture(filepath):
        # text_reader = easyocr.Reader(['en','bn'])
        # file=Path(filepath)
        # if file.is_file():
        #     print(f"Got the image. Filepath: {filepath}")
        #     result_from_text = text_reader.readtext(filepath)
        #     full_text=[]
        #     for (bbox, text, prob) in result_from_text:
        #         print(f'Text: {text}, Probability: {prob}')
        #         if(bool(regex.fullmatch(r'\P{L}*\p{Bengali}+(?:\P{L}+\p{Bengali}+)*\P{L}*', text))):
        #             full_text.append(text + "। ")
        #         else:
        #             full_text.append(text+". ")
        #     print(full_text)
                
        # else:
        #     print("There was no image found with the filepath")
        pass

def exampleScheduler():
    print("Scheduling tasks")

def systemOperations(request):
    
    print("Choose operations to perform. Enter 0 to exit the program")
    
    while True:
        print("1. Register users from CSV files")
        print("2. Run the scheduler")
        print("3. Extract Text from Images")
        print("4. Process a particular complain ID")
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
        elif(choice==2):
            # trigger the scheduler
            # ModelOperations.start_scehduler()
            scheduler=BlockingScheduler()
            job_id=scheduler.add_job(exampleScheduler, 'interval', seconds=5)
            scheduler.start()
            
        elif(choice==3):
            # extract text from images
            filepath=str(input("Enter file path: "))
            example_extract_text_from_picture(filepath=filepath)
        elif(choice==4):
            complain_id=int(input("Enter the complain ID you want to process: "))
            try:
                operation=DataProcessingAndOperations
                operation.scheduler.start()
                operation.startSchedulingProgramms(complain_id=complain_id)
            except Exception as e:
                print(e)
                # operation.scheduler.shutdown(wait=False)
                # operation.scheduler.start()
                # operation.startSchedulingProgramms(complain_id=complain_id)
                
    return render(request,"index.html")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getUserComplains(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        data=request.data
        # get the complainer
        user_id=request.user.username
        # get user object
        try:
            user=UserInformations.objects.get(user_id=user_id)
        except UserInformations.DoesNotExist:
            return Response({'msg':"Session timed out. Please login again!"},status=status.HTTP_400_BAD_REQUEST)
        
        complaints = UserComplains.objects.filter(complainer=user).values().order_by('-id')
        return Response({'complain_list':complaints},status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getComplainDetails(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        data=request.data
        # get the complain id
        complain_id=data.get('complain_id')
        # get the complain object
        try:
            complain=UserComplains.objects.get(pk=complain_id)
            proof_images=UserComplainProof.objects.filter(complain_id=complain)
            bully_images=BullyPictures.objects.filter(complain_id=complain)
            
            cyber_bullying_flag_picture_urls=[]
            
            if(complain.complain_cyberBullying_flag_validation):
                for bullying_picture in proof_images:
                    try:
                        cyber_bullying_flag_picture_urls.append(bullying_picture.cyber_bullying_flag_picture.url)
                    except Exception as e:
                        pass
            proof_images_urls = [proof_image.proof.url for proof_image in proof_images]
            bully_images_urls = [bully_image.bully_image.url for bully_image in bully_images]            
            return Response({
                'proof_images':proof_images_urls,
                'bully_images':bully_images_urls,
                'flagged_images':cyber_bullying_flag_picture_urls,
                'organization_name':complain.organization_id.name,
                'complain_cyberBullying_flag_validation':complain.complain_cyberBullying_flag_validation,
                'complain_description':complain.complain_description,
                'is_bully_guilty':complain.guilty,
                'proctor_decision':complain.proctor_decision,
                'complain_type':complain.complain_type.complain_type,
                'bully_id':complain.bully_id,
                'complain_status':complain.complain_status,
                'is_meeting_scheduled':complain.is_meeting_scheduled,
                },status=status.HTTP_200_OK)
        except UserComplains.DoesNotExist:
            return Response({'msg':"Complain not found!"},status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateComplainDetails(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        data=request.data
        # get the complain id
        complain_id=data.get('complain_id')
        try:
            # get the complain object
            complain = UserComplains.objects.get(pk=complain_id)
            # update the complain attributes
            complain.proctor_decision=data.get('proctor_decision')
            complain.complain_status=data.get('complain_status')
            complain.guilty=data.get('is_bully_guilty')
            complain.save()
            return Response({'msg':"Complain updated successfully!"},status=status.HTTP_200_OK)
        except UserComplains.DoesNotExist:
            return Response({'msg':"Complain not found!"},status=status.HTTP_404_NOT_FOUND)

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
            # start the task scheduler to process the complains
            try:
                operation=DataProcessingAndOperations
                operation.scheduler.start()
                operation.startSchedulingProgramms(complain_id=complain_pk)
            except Exception as e:
                print(e)
                operation.scheduler.shutdown(wait=False)
                operation.scheduler.start()
                operation.startSchedulingProgramms(complain_id=complain_pk)

            return Response({'msg': "Complain Registered! We will get back to you soon!"},status=status.HTTP_200_OK)
        else:
            return Response({'msg': "Complain can not be registered!"},status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def proctorComplainView(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        # get the userid
        user_id=request.user.username
        # get the user info and check if the user is a proctor or not
        try:
            user=UserInformations.objects.get(user_id=user_id)
            if(user.is_proctor):
                # get all the complains of that particular organization
                organization_complains=UserComplains.objects.filter(organization_id=user.organization_id).values(
                    'id','complainer','organization_id','complain_type',
                    'bully_name','bully_id',
                    'incident_date','complain_description','complain_cyberBullying_flag_validation',
                    'complain_status','proctor_decision','guilty'
                ).order_by('-pk')
                return Response({'complain_list':organization_complains,'organization_name':user.organization_id.name},status=status.HTTP_200_OK)
            else:
                print("User is not a proctor")
                return Response({'msg':"You need proctor access to view this page!"},status=status.HTTP_401_UNAUTHORIZED)
        except UserInformations.DoesNotExist:
            return Response({'msg':"User not found!"},status=status.HTTP_404_NOT_FOUND)
        

class ScheduleMeeting(APIView):
    @permission_classes([IsAuthenticated])
    
    def get(self,request):
        if not request.user.is_authenticated:
            return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # get username
            user_id=request.user.username
            # get all the scheduled meetings for the user
            try:
                user_scheduled_meetings=ScheduledMeetings.objects.filter(user_id=user_id).values().order_by('meeting_time')
                scheduled_meeting_complain_list_id=[]
                for complains in user_scheduled_meetings:
                    scheduled_meeting_complain_list_id.append(complains['complain_id_id'])
                complain_details=UserComplains.objects.filter(pk__in=scheduled_meeting_complain_list_id).values()
                return Response({'sceduled_meetings':user_scheduled_meetings,'complain_details':complain_details},status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({'msg':"User not found!"},status=status.HTTP_404_NOT_FOUND)
    
    def post(self,request):
        if not request.user.is_authenticated:
            return Response({'msg': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data=request.data
            task=data.get('task')
            if(task=='meeting_setup'):
                complain_id=data.get('complain_id')
                # get the complain object to get the information about complainer and bully
                try:
                    complain=UserComplains.objects.get(id=complain_id)
                    complainer_contact_no=complain.complainer.contact_no
                    complainer_email=complain.complainer.email_address
                    # now we need to try and get the informations about bully
                    bully_id=complain.bully_id
                    # get information about bully from user database
                    try:
                        bully=UserInformations.objects.get(user_id=bully_id)
                        bully_contact_no=bully.contact_no
                        bully_email=bully.email_address
                        
                        return Response({
                            'msg':"Got contact informations of both parties from user database",
                            'complainer_contact_no':complainer_contact_no,
                            'complainer_email':complainer_email,
                            'bully_contact_no':bully_contact_no,
                            'bully_email':bully_email,
                            'is_meeting_scheduled':complain.is_meeting_scheduled,
                        },status=status.HTTP_200_OK)
                    except UserInformations.DoesNotExist:
                        return Response({
                                'msg':"Could not get bully information from user database",
                                'complainer_contact_no':complainer_contact_no,
                                'complainer_email':complainer_email,
                                'bully_contact_no':'',
                                'bully_email':''
                                },status=status.HTTP_200_OK)       
                except UserComplains.DoesNotExist:
                    return Response({'msg':"Complain not found!"},status=status.HTTP_404_NOT_FOUND)
            elif(task=='call_meeting'):
                complain_id=data.get('complain_id')
                # get the complain object
                complain=UserComplains.objects.get(pk=complain_id)
                meeting_time=data.get('meeting_time')
                meeting_message=data.get('meeting_message')
                '''schedule meetings for- 
                1.Proctor, 2. Complainer, 3. Bully'''
                # get the proctor id first. as the proctor sets up the meeting, its going to be the current user id.
                proctor_id=request.user.username
                # schedule the meeting for proctor
                try:
                    new_proctor_meeting=ScheduledMeetings.objects.create(
                        complain_id=UserComplains.objects.get(pk=complain_id),
                        user_id=UserInformations.objects.get(user_id=proctor_id),
                        meeting_time=meeting_time,
                        meeting_message=meeting_message,
                    )
                    new_proctor_meeting.save()
                except Exception as e:
                    print(e)                
                # schedule meeting for complainer
                try:                    
                    new_complainer_meeting=ScheduledMeetings.objects.create(
                        complain_id=complain,user_id=complain.complainer,
                        meeting_time=meeting_time,
                        meeting_message=meeting_message,
                    )
                    new_complainer_meeting.save()
                except Exception as e:
                    print(e)
                try:
                    # get the bully object from user informations
                    try:
                        bully=UserInformations.objects.get(user_id=complain.bully_id)
                        new_bully_meeting=ScheduledMeetings.objects.create(
                            complain_id=complain,user_id=bully,
                            meeting_time=meeting_time,
                            meeting_message=meeting_message,  
                        )
                        new_bully_meeting.save()
                    except UserInformations.DoesNotExist:
                        complain.is_meeting_scheduled=True
                        complain.save()
                        return Response({'msg':"Could not get bully information from user database. Meeting Scheduled for Complainer and Proctor. Bully will be notified by the given contact details!"},status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                
                complain.is_meeting_scheduled=True
                complain.save()
                return Response({'msg':"Meeting was scheduled for all the parties"},status=status.HTTP_200_OK)

                                    
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

class ChatbotAPI(APIView):    
    @permission_classes([IsAuthenticated])
    
    def get(self,request):
        if not request.user.is_authenticated:
            return Response({'msg': 'User is not authenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            previous_message_status,user_chat_list,assistant_chat_list,msg=Chatbot.getAllMessagesOfUser(request.user.username)
            if(previous_message_status):
                return Response({'user_chat_list':user_chat_list,'assistant_chat_list':assistant_chat_list,'msg': msg}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': msg}, status=status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        if not request.user.is_authenticated:
            return Response({'msg': 'User is not authenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data=request.data
            user_message=data.get('user_message')
            user_id=request.user.username
            bot_status,message=Chatbot.generateAssistantMessages(user_message=user_message,user_id=user_id)
            if(bot_status):
                return Response({'msg':f"{message}"},status=status.HTTP_200_OK)
            else:
                return Response({'msg':f"{message}"},status=status.HTTP_400_BAD_REQUEST)
            
