from apscheduler.schedulers.background import BlockingScheduler
from .models import *
from pathlib import Path
from .image_processing import ProcessImageForOCR
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
        
        DataProcessingAndOperations.processImagesToExtractTexts(image_objects=pictures,scheduler=scheduler)
        
        
    def processImagesToExtractTexts(image_objects,scheduler):
        
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
                processed_image=ProcessImageForOCR.processImage(imageFile=image_file,fileExtension=file_extension,filename=file_name)
                print("Image Processing Performed. Saving those Processed Images Now")
                get_image_proof_id=UserComplainProof.objects.get(pk=image.pk)
                get_image_proof_id.processed_proof_image=processed_image
                get_image_proof_id.save()
                
        print(f"Image saved successfully. Now, let's extract texts")
        scheduler.shutdown(wait=False)
    
    def extractStringsFromImages(image_path):
        pass
    def cyberBullyingIdentification(string):
        pass
    
    