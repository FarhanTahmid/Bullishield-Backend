from apscheduler.schedulers.background import BlockingScheduler
import time
from .models import *
from pathlib import Path
from .processor import OCRActions,TextProcessor
from .cyberbullying_classifiers import *

import os


class DataProcessingAndOperations:
    
    def startSchedulingProgramms(complain_id):
        
        scheduler=BlockingScheduler()
        job_id=scheduler.add_job(DataProcessingAndOperations.getComplainToProcess,'interval',seconds=5,args=[complain_id,scheduler])
        scheduler.start()
        # job_id.remove()
        # scheduler.shutdown(wait=False)

    def getComplainToProcess(complain_id,scheduler):
        
        print(f"Task is running after 5 seconds. Got the complain ID: {complain_id}")
        
        get_complain=UserComplains.objects.get(pk=complain_id)
        
        print(f"Got the Complain: {get_complain}")
        
        # get the proof pictures associated with the complain
        pictures=UserComplainProof.objects.filter(complain_id=get_complain)
        
        print(f"Total Picture found with the complain: {len(pictures)}. They are passed to processing now.")
        
        DataProcessingAndOperations.processImagesToExtractTexts(complain_id=complain_id,image_objects=pictures,scheduler=scheduler)
        
        
    def processImagesToExtractTexts(complain_id,image_objects,scheduler):
        
        print(f"Got images to process: {image_objects}")
        
        for image in image_objects:
            image_file=Path(image.proof.path)
            if(image_file.is_file()):
                print(f"Found the image file: {image_file}")
                print("Processing the Image file now!")
                # Get the base name of the file
                base_name = os.path.basename(image_file)
                # Split the base name into name and extension
                file_name, file_extension = os.path.splitext(base_name)
                file_extension = file_extension.lstrip('.').upper()
                processed_image=OCRActions.processImage(imageFile=image_file,fileExtension=file_extension,filename=file_name)
                print("Image Processing Performed. Saving those Processed Images Now")
                get_image_proof_id=UserComplainProof.objects.get(pk=image.pk)
                get_image_proof_id.processed_proof_image=processed_image
                get_image_proof_id.save()
                
        print(f"Image saved successfully. Now, let's extract texts")
        time.sleep(5)
        DataProcessingAndOperations.extractStringsFromImages(complain_id=complain_id,scheduler=scheduler)
        
    
    def extractStringsFromImages(complain_id,scheduler):
        complain_objects=UserComplainProof.objects.filter(complain_id=UserComplains.objects.get(id=complain_id))
        
        for object in complain_objects:
            print(object.processed_proof_image.path)
            processed_image_file=Path(object.processed_proof_image.path)
            if(processed_image_file.is_file()):
                print(f"Found the processed image file: {processed_image_file}")
                print("Extracting Texts from File Now!")
                extraction=OCRActions.extractTexts(image=object.processed_proof_image.path,proof_object=object)
                if(extraction):
                    print("All Extraction Completed! Now identify CyberBullying")
                else:
                    print("Extraction Failed!")
            else:
                print("File Not Found")
        print("Now Lets Process the Texts")
        DataProcessingAndOperations.cyberBullyingIdentification(complain_id=complain_id,scheduler=scheduler)

    def cyberBullyingIdentification(complain_id,scheduler):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # load cyberBullying models
        english_model=CyberBullyingClassifierEnglish()
        english_model.to(device=device)
        english_model.load_state_dict(torch.load('Models/english_bert.pth'))
        bangla_model=CyberBullyingClassifierBangla()
        bangla_model.to(device=device)
        bangla_model.load_state_dict(torch.load('Models/bangla_bert.pth'))
        
        # get the images associated with the complain object
        proof_image_objects=UserComplainProof.objects.filter(complain_id=UserComplains.objects.get(pk=complain_id))
        # get the image strings asscociated with the image object of the complain
        for image_object in proof_image_objects:
            extracted_string_objects=ComplainProofExtractedStrings.objects.filter(image_id=image_object)
            for string in extracted_string_objects:
                print(f"Extracted From Image object:{image_object}, Raw String:{string.extracted_strings}")
                string.extracted_strings,bullying_flag=TextProcessor.textProcessor(string=string.extracted_strings,device=device,english_model=english_model,bangla_model=bangla_model)
                string.cyberBullyingFlag=bullying_flag
                string.save()
                if(string.extracted_strings=='' or string.extracted_strings==' '):
                    # delete the string object as it is null
                    string.delete()
        print("All cyber bullying prediction Done!")                  
        scheduler.shutdown(wait=False)

    
    