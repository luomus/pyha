import schedule
from threading import Thread
from time import sleep
from pyha.management.commands import missing_handlers_email, timed_email, decline_overdue_collections


def timed_email():
    c = timed_email.Command()
    c.handle()
    
def missing_handlers_email():
    c = missing_handlers_email.Command()
    c.handle()
    
def decline_overdue_collections():
    c = decline_overdue_collections.Command()
    c.handle()
            
def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()
    

def scheduler():   
    
    # set the events here
    schedule.every().day.at("11:22").do(run_threaded, timed_email) 
    schedule.every().tuesday.at("11:22").do(run_threaded, missing_handlers_email)
    # For schedule function usage:
    # ---- https://schedule.readthedocs.io/en/stable/index.html ----
    
    while True:
        schedule.run_pending()
        sleep(1)



schedule_thread = Thread(target=scheduler)
schedule_thread.start()