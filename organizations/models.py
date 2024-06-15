from django.db import models

# Create your models here.

class OrganizationTypes(models.Model):
    
    '''Stores the type of organizations.'''
    
    type=models.CharField(null=False,blank=False,max_length=50)
    
    class Meta:
        verbose_name="Organization Type"
    
    def __str__(self) -> str:
        return self.type
    

class OrganizationData(models.Model):
    
    '''Stores the information about the Organization.'''
    
    name=models.CharField(null=False,blank=False,max_length=100)
    type=models.ForeignKey(OrganizationTypes,null=False,blank=False,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name="Organizations"
    
    def __str__(self) -> str:
        return self.name
