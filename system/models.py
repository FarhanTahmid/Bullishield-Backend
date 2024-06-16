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
        return str(self.pk)

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
    bully_picture=models.ImageField(null=True,blank=True,upload_to='bully_pictures/')    
    
    #information of the complaing
    incident_date=models.DateField(null=True,blank=True)
    complain_description=models.TextField(null=False,blank=False,max_length=1000)
    complain_validation=models.BooleanField(null=False,blank=False,default=False)
    complain_status=models.CharField(null=False,blank=False,default="Processing",max_length=30)
    proctor_decision=models.CharField(null=True,blank=True,max_length=1000)
    
    guilty=models.BooleanField(null=True,blank=True,default=False)

    class Meta:
        verbose_name="User Complains"

    def __str__(self) -> str:
        return str(self.pk)

class UserComplainProof(models.Model):
    '''Stores the uploaded complain proves'''
    complain_id=models.ForeignKey(UserComplains,null=False,blank=False,on_delete=models.CASCADE)
    proof=models.ImageField(null=True,blank=True,upload_to=f'complain_proofs/{complain_id}/')
    proof_image_to_text=models.CharField(null=True,blank=True,max_length=400)

    class Meta:
        verbose_name = ("Complain Proves")
    def __str__(self):
        return str(self.complain_id)
   