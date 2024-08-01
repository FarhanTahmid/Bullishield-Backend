from apscheduler.schedulers.background import BlockingScheduler,BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import time
from .models import *
from pathlib import Path
from .processor import OCRActions,TextProcessor
from .cyberbullying_classifiers import *
import json
import os


class DataProcessingAndOperations:
    
    # Initialize the scheduler with appropriate executors
    executors = {
        'default': ThreadPoolExecutor(10),
        'processpool': ProcessPoolExecutor(3)
    }
    # scheduler to automate tasks
    scheduler=BackgroundScheduler(executors=executors)
    scheduler.start()
    
    def startSchedulingProgramms(complain_id):
        # add job to scheduler to run all programs
        if(DataProcessingAndOperations.scheduler.running):
            job_id=DataProcessingAndOperations.scheduler.add_job(DataProcessingAndOperations.getComplainToProcess,trigger=IntervalTrigger(seconds=5),args=[complain_id])
        else:
            print("Scheduler is not running")
        
    def stopScheduler():
        # to stop the scheduler after a run
        if(DataProcessingAndOperations.scheduler.running):
            DataProcessingAndOperations.scheduler.shutdown(wait=False)
            print("Scheduler is stopped!")


    def getComplainToProcess(complain_id):
        # get the complain object
        get_complain=UserComplains.objects.get(pk=complain_id)
        # get the proof pictures associated with the complain object
        pictures=UserComplainProof.objects.filter(complain_id=get_complain)
        # we now process the image to extract texts
        DataProcessingAndOperations.processImagesToExtractTexts(complain_id=complain_id,image_objects=pictures)
        
    def processImagesToExtractTexts(complain_id,image_objects):
        
        # traverse through all the image objects the complain was associated with 
        for image in image_objects:    
            # get the path of the image. Remember its not a file URL, rather a binary file
            image_file=Path(image.proof.path)
            
            if(image_file.is_file()):
                
                # Get the base name of the file
                base_name = os.path.basename(image_file)
                # Split the base name into name and extension
                file_name, file_extension = os.path.splitext(base_name)
                # strip the (.) from the file extension
                file_extension = file_extension.lstrip('.').upper()
                
                # get the processed Image from the function
                processed_image=OCRActions.processImage(imageFile=image_file,fileExtension=file_extension,filename=file_name)
                
                # store the image with the associated Complain Proof object
                get_image_proof_id=UserComplainProof.objects.get(pk=image.pk)
                get_image_proof_id.processed_proof_image=processed_image
                get_image_proof_id.save()
        
        # to delay the program for 5 seconds after all images are processed 
        time.sleep(5)
        # call function to extract string from the images
        DataProcessingAndOperations.extractStringsFromImages(complain_id=complain_id)
        
    
    def extractStringsFromImages(complain_id):
        # get the complain proof objects
        complain_objects=UserComplainProof.objects.filter(complain_id=UserComplains.objects.get(id=complain_id))
        
        # traverse through the objects
        for object in complain_objects:
            # get the processed image Path associated with the object
            processed_image_file=Path(object.processed_proof_image.path)
            if(processed_image_file.is_file()):
                
                # extract texts performing the OCR method
                extraction=OCRActions.extractTexts(image=object.processed_proof_image.path,proof_object=object)
                
                if(extraction): #if true
                    pass
                else:
                    print("Extraction Failed!")
                    DataProcessingAndOperations.stopScheduler() #stop scheduler if extraction of text fails
            else:
                print("File Not Found")
        
        # move to the next step of cyberbullying detection
        DataProcessingAndOperations.cyberBullyingIdentification(complain_id=complain_id)

    def cyberBullyingIdentification(complain_id):
        # first get the device the program is running on, CPU OR cuda
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # load the cyberBullying models.
        
        # english model
        english_model=CyberBullyingClassifierEnglish()
        english_model.to(device=device)
        english_model.load_state_dict(torch.load('Models/english_bert.pth'))
        
        # bangla model
        bangla_model=CyberBullyingClassifierBangla()
        bangla_model.to(device=device)
        bangla_model.load_state_dict(torch.load('Models/bangla_bert.pth'))
        
        # get the images associated with the complain object
        proof_image_objects=UserComplainProof.objects.filter(complain_id=UserComplains.objects.get(pk=complain_id))
        
        # traverse through the proof objects
        for image_object in proof_image_objects:
            
            # get the extracted strings asscociated with the image object of the complain
            extracted_string_objects=ComplainProofExtractedStrings.objects.filter(image_id=image_object)
            
            # traverse through the extracted string objects
            for string in extracted_string_objects:
                # get extracted string and bullying flag from text processors
                string.extracted_strings,bullying_flag=TextProcessor.textProcessor(string=string.extracted_strings,device=device,english_model=english_model,bangla_model=bangla_model)
                # mark with cyberbullying Flag
                string.cyberBullyingFlag=bullying_flag
                string.save()
                
                # delete the string object if it is null or empty
                if(string.extracted_strings=='' or string.extracted_strings==' '):
                    string.delete()
                    
        # generate image to identify bullying texts
        DataProcessingAndOperations.generateProofOfBullyingMessage(complain_id=complain_id)
    
    def generateProofOfBullyingMessage(complain_id):
        
        # get the complain proof objects
        proof_objects=UserComplainProof.objects.filter(complain_id=complain_id)
        
        for proof in proof_objects:
            # now get the strings which are flagged as cyberBullying in the ExtractedStringModel
            extracted_bullying_strings=ComplainProofExtractedStrings.objects.filter(
                image_id=proof.pk,cyberBullyingFlag=True
            )
            # check if there is any flagged objects
            if(len(extracted_bullying_strings)>0):
                
                bbox_list=[] #to store the bbox dimensions for text markup
                
                for string in extracted_bullying_strings:
                    bbox_list.append(json.loads(string.bbox)) 
                
                # get the image file
                image_file=Path(proof.processed_proof_image.path)
                # Get the base name of the file
                base_name = os.path.basename(image_file)
                # Split the base name into name and extension
                file_name, file_extension = os.path.splitext(base_name)
                file_extension = file_extension.lstrip('.').upper()
                
                # get the markedup flagged image
                flagged_image=OCRActions.cyberBullyingFlaggedImageProcess(
                    imageFile=Path(proof.processed_proof_image.path),
                    fileExtension=file_extension,
                    filename=file_name,bbox_list=bbox_list
                )
                # update flag picture and cyberBullying Flag for the picture
                proof.cyber_bullying_flag_picture=flagged_image
                proof.cyber_bullying_flag=True
                proof.save()
                
                # Update main complain status and bullying flag
                complain=UserComplains.objects.get(pk=complain_id)
                complain.complain_cyberBullying_flag_validation=True
                complain.complain_status="Validation Completed"
                complain.save()
            else:
                # update bullying flag to false if no bullying is founc
                proof.cyber_bullying_flag=False
                proof.save()
                
                # Update main complain status and bullying flag
                complain=UserComplains.objects.get(pk=complain_id)
                complain.complain_status="Validation Completed"
                complain.save()
        
        # shutdown scheduler to end all process
        DataProcessingAndOperations.stopScheduler()        

    
    