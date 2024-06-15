from user.user_registration import UserRegistration
from organizations.models import OrganizationData


class SystemOperations:

    def register_user_with_csv():
        
        print('\n')
        print("###############################")
        print("Register Members with CSV Files")
        print("###############################")
        
        print("Registered Organizations in the System: ")
        get_existing_org_types=OrganizationData.objects.all().order_by('pk')
        for organisations in get_existing_org_types:
            print(f"{organisations.pk}. {organisations.name}")
        
        organization_pk=int(input("\nEnter organization: "))
        filepath=str(input("Enter the full filepath of CSV: "))

        result=UserRegistration.userRegistrationFromCSV(organization_key=organization_pk,filepath=filepath)        
        
        return result