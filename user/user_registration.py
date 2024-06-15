import csv
from .models import *
from organizations.models import OrganizationData

class UserRegistration:
    
    def userRegistrationFromCSV(organization_key,filepath):
        '''
            takes input:
            -organization_key: pk value of the organization the user is going to go registered with
            -filepath: path to the csv file containing user data
        '''
        # get the organization
        organization=OrganizationData.objects.get(pk=organization_key)
        
        try:
            with open(filepath,'r') as file_data:
                file_reader=csv.reader(file_data)
                for row in file_reader:
                    try:
                        new_user=UserInformations(
                            user_id=row[0],
                            organization_id=organization,
                            full_name=row[1],
                            birth_date=row[2],
                            contact_no=row[3],
                            email_address=row[4],
                            home_address=row[5],
                            gender=row[6]
                        )
                        new_user.save()
                    except Exception as e:
                        print(e)
            return True
        except Exception as e:
            print(e)
            return False
                
            