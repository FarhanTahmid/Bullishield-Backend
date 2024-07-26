from apscheduler.schedulers.background import BlockingScheduler
from .models import SchedulerRecords
import easyocr
from pathlib import Path
import easyocr
import regex


scheduler=BlockingScheduler()

class ModelOperations:
    
    def extract_text_from_picture(filepath):
        text_reader = easyocr.Reader(['en','bn'])
        file=Path(filepath)
        if file.is_file():
            print(f"Got the image. Filepath: {filepath}")
            result_from_text = text_reader.readtext(filepath)
            full_text=[]
            for (bbox, text, prob) in result_from_text:
                print(f'Text: {text}, Probability: {prob}')
                if(bool(regex.fullmatch(r'\P{L}*\p{Bengali}+(?:\P{L}+\p{Bengali}+)*\P{L}*', text))):
                    full_text.append(text + "। ")
                else:
                    full_text.append(text+". ")
            print(full_text)
                
        else:
            print("There was no image found with the filepath") 
    
    def start_scehduler():
        newSchedulerLog=SchedulerRecords.objects.create(job_id="New job")
        newSchedulerLog.save()
        job_id=scheduler.add_job(ModelOperations.extract_image_from_picture, 'interval', seconds=5,args=[job_id,newSchedulerLog])
        scheduler.start()
        return True