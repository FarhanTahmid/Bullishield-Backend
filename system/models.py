from django.db import models
from user.models import UserInformations
from organizations.models import OrganizationData
# Create your models here.

class Complain_types(models.Model):
    '''Stores the complain type'''
    complain_type=models.CharField(null=False,blank=False,max_length=30)

    class Meta:
        verbose_name="Complain Type"

    def __str__(self) -> str:
        return str(self.complain_type)

class UserComplains(models.Model):
    '''
    Stores all the necessary informations for user complains
    '''
    #complainer is the username of the user who is lodging the complain
    complainer=models.ForeignKey(UserInformations,null=False,blank=False,on_delete=models.CASCADE)
    #organization_id is the id of the organization from which the user belongs
    organization_id=models.ForeignKey(OrganizationData,null=False,blank=False,on_delete=models.CASCADE)    
    complain_type=models.ForeignKey(Complain_types,null=True,blank=True,on_delete=models.CASCADE)
    
    # information of the bully
    bully_name=models.CharField(null=False,blank=False,max_length=50,default="Unknown")
    bully_id=models.CharField(null=True,blank=True,max_length=30)
    
    #information of the complaing
    incident_date=models.DateField(null=True,blank=True)
    complain_description=models.TextField(null=False,blank=False,max_length=1000)
    complain_validation=models.BooleanField(null=False,blank=False,default=False)
    complain_status=models.CharField(null=False,blank=False,default="Processing",max_length=30)
    proctor_decision=models.CharField(null=True,blank=True,max_length=1000)
    
    guilty=models.BooleanField(null=True,blank=True,default=False)
    is_meeting_scheduled=models.BooleanField(null=False,blank=False,default=False)
    
    
    class Meta:
        verbose_name="User Complains"

    def __str__(self) -> str:
        return str(self.pk)


def bully_image_upload_to(instance, filename):
    return f'bully_image/{instance.complain_id}/bully_{filename}'
class BullyPictures(models.Model):
    '''Stores the pictures of the bully in the system'''
    complain_id=models.ForeignKey(UserComplains,null=False,blank=False,on_delete=models.CASCADE)
    bully_image=models.ImageField(null=True,blank=True,upload_to=bully_image_upload_to)
    
    class Meta:
        verbose_name="Bully Images"
    def __str__(self) -> str:
        return str(self.complain_id)

def prove_image_upload_to(instance, filename):
    return f'complain_proofs/{instance.complain_id}/prove_{filename}'

def prove_processed_image_upload_to(instance,filename):
    return f'complain_proofs/{instance.complain_id}/processed_image_{filename}'

class UserComplainProof(models.Model):
    '''Stores the uploaded complain proves'''
    complain_id=models.ForeignKey(UserComplains,null=False,blank=False,on_delete=models.CASCADE)
    proof=models.ImageField(null=True,blank=True,upload_to=prove_image_upload_to)
    processed_proof_image=models.ImageField(null=True,blank=True,upload_to=prove_processed_image_upload_to)
    proof_image_to_text=models.CharField(null=True,blank=True,max_length=400)

    class Meta:
        verbose_name = "Complain Proves"
    def __str__(self):
        return str(self.complain_id)


class ComplainProofExtractedStrings(models.Model):
    '''Stores the strings extracted from images. Every string extracted from images is stored separately to identify if there are any cyberbullying texts'''
    image_id=models.ForeignKey(UserComplainProof,null=False,blank=False,on_delete=models.CASCADE)
    extracted_strings=models.TextField(null=True,blank=True)
    prediction_confidence=models.DecimalField(null=True,blank=True,decimal_places=4,max_digits=10)
    
    class Meta:
        verbose_name="Extracted Texts From Images"
    
    def __str__(self) -> str:
        return str(self.pk)

class ScheduledMeetings(models.Model):
    '''Stores the scheduled meetings between the bully and the complainer'''
    complain_id=models.ForeignKey(UserComplains,null=False,blank=False,on_delete=models.CASCADE)
    user_id=models.ForeignKey(UserInformations,null=False,blank=False,on_delete=models.CASCADE)
    meeting_time=models.DateTimeField(null=False,blank=False)
    meeting_message=models.CharField(max_length=1000,null=False,blank=False)
    
    class Meta:
        verbose_name = "Scheduled Meetings"
    def __str__(self):
        return str(self.pk)

class Notifications(models.Model):
    '''Stores the notifications sent to the user'''
    user_id=models.ForeignKey(UserInformations,null=False,blank=False,on_delete=models.CASCADE)
    notification_message=models.CharField(max_length=300,null=False,blank=False)
    is_seen=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="User Notifications"
    def __str__(self):
        return str(self.pk)

class ChatbotThreads(models.Model):
    '''Stores the chatbot threads for every users'''
    user_id=models.OneToOneField(UserInformations,null=False,blank=False,on_delete=models.CASCADE)
    thread_id=models.CharField(models.CharField,null=False,blank=False,max_length=100)
    
    class Meta:
        verbose_name = "Chatbot Threads"
    def __str__(self) -> str:
        return str(self.pk)


class SchedulerRecords(models.Model):
    '''Stores Scheduler Records in the background'''
    job_id=models.CharField(null=False,blank=False,max_length=300)
    complain_id=models.ForeignKey(UserComplains,null=True,blank=True,on_delete=models.CASCADE)
    execution_status=models.BooleanField(null=False,blank=False,default=False)
    class Meta:
        verbose_name="Scheduler Records"
    def __str__(self) -> str:
        return str(self.pk)
