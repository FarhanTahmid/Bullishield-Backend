from .models import *

class ComplainHandler():
    
    def createComplains(complainer_id,complain_type_id,bully_name,bully_id,incident_date,complain_description):
        '''
            arguments:
            complainer_id: str id
            complain_type_id: str id
            bully_name: str
            bully_id: str id
            incident_date: str format(YYY-MM-DD)
            description: str
        '''
        # first get the complainer object
        try:
            complainer = UserInformations.objects.get(user_id=complainer_id)            
        except UserInformations.DoesNotExist:
            return False
        try:
            new_complain=UserComplains.objects.create(
                complainer=complainer,
                organization_id=complainer.organization_id,
                complain_type_id=complain_type_id,
                bully_name=bully_name,bully_id=bully_id,
                incident_date=incident_date,
                complain_description=complain_description,   
            )
            new_complain.save()
            return True,new_complain.pk
        except Exception as e:
            print(e)
            return False
    
        
        
        
        