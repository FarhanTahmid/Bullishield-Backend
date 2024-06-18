from .models import *

class ComplainHandler():
    
    def createComplains(complainer_id,complain_type_id,bully_name,bully_id,bully_picture,incident_date,complain_description):
        
        # first get the complainer object
        try:
            complainer = UserInformations.objects.get(user_id=complainer_id)
        except UserInformations.DoesNotExist:
            return False
        try:
            new_complain=UserComplains.objects.create(
                complainer=complainer,
                organization_id=complainer.organization_id,
                complain_type_id=Complain_types.objects.get(pk=complain_type_id),
                bully_name=bully_name,bully_id=bully_id,bully_picture=bully_picture,
                incident_date=incident_date,
                complain_description=complain_description,   
            )
            new_complain.save()
            return True
        except Exception as e:
            print(e)
            return False
    
        
        
        
        