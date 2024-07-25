from apscheduler.schedulers.background import BlockingScheduler
from .models import SchedulerRecords

scheduler=BlockingScheduler()

class ModelOperations:
    
    def extract_image_from_picture(job_id,schedulerLog):
        print("Extracting Images from picture, written in models")
        print(job_id)
        schedulerLog.execution_status=True
        schedulerLog.job_id=job_id
        schedulerLog.save()
        scheduler.shutdown(wait=False)
    
    
    def start_scehduler():
        newSchedulerLog=SchedulerRecords.objects.create(job_id="New job")
        newSchedulerLog.save()
        job_id=scheduler.add_job(ModelOperations.extract_image_from_picture, 'interval', seconds=5,args=[job_id,newSchedulerLog])
        scheduler.start()
        return True