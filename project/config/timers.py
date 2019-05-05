import schedule
from django.db import connection
from threading import Thread
from time import sleep
from pyha.management.commands.timed_email import Command as TimedEmailCommand
from pyha.management.commands.missing_handlers_email import Command as MissingHandlersCommand
from pyha.management.commands.decline_overdue_collections import Command as DeclineOverDueCollectionsCommand

def timed_email():
    c = TimedEmailCommand()
    c.handle()
    connection.close()
    
def missing_handlers_email():
    c = MissingHandlersCommand()
    c.handle()
    connection.close()
    
def decline_overdue_collections():
    c = DeclineOverDueCollectionsCommand()
    c.handle()
    connection.close()
            
def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()
    

def scheduler():   
    
    # set the events here   
    #Poistakaa nama kommenteista, niin lahtee arkipaivina kasittelijoiden viestit
    #schedule.every().monday.at("11:22").do(run_threaded, timed_email) 
    #schedule.every().tuesday.at("11:22").do(run_threaded, timed_email) 
    #schedule.every().wednesday.at("11:22").do(run_threaded, timed_email) 
    #schedule.every().thursday.at("11:22").do(run_threaded, timed_email) 
    #schedule.every().friday.at("11:22").do(run_threaded, timed_email) 
    
    schedule.every().tuesday.at("11:22").do(run_threaded, missing_handlers_email)
    # For schedule function usage:
    # ---- https://schedule.readthedocs.io/en/stable/index.html ----
    
    while True:
        schedule.run_pending()
        sleep(1)



schedule_thread = Thread(target=scheduler)
schedule_thread.daemon = True
schedule_thread.start()