from django.shortcuts import render,redirect
from .system_functions import SystemOperations
# Create your views here.

def systemOperations(request):
    
    print("Choose operations to perform. Enter 0 to exit the program")
    
    while True:
        print("1. Register users from CSV files")
        print("2. Create Organization Types")
        print("3. Create Organizations")
        
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


    return render(request,"index.html")