import schedule
from django.db import connection
from threading import Thread
from time import sleep
from pyha.management.commands.timed_email import Command as TimedEmailCommand
from pyha.management.commands.timed_email_to_requesters import Command as TimedEmailToRequestersCommand
from pyha.management.commands.missing_handlers_email import Command as MissingHandlersCommand
from pyha.management.commands.decline_overdue_collections import Command as DeclineOverDueCollectionsCommand
from pyha.management.commands.check_failed_requests import Command as CheckFailedRequestsCommand
from pyha.management.commands.update_statistics_cache import Command as UpdateStatisticsCacheCommand
from pyha.models import AdminPyhaSettings


def timed_email():
    pyha_settings = AdminPyhaSettings.objects.filter(settingsName='default')
    if pyha_settings.exists():
        if pyha_settings.first().enableDailyHandlerEmail:
            c = TimedEmailCommand()
            c.handle()
            connection.close()


def timed_email_to_requesters():
    pyha_settings = AdminPyhaSettings.objects.filter(settingsName='default')
    if pyha_settings.exists():
        if pyha_settings.first().enableDailyRequesterEmail:
            c = TimedEmailToRequestersCommand()
            c.handle()
            connection.close()


def missing_handlers_email():
    pyha_settings = AdminPyhaSettings.objects.filter(settingsName='default')
    if pyha_settings.exists():
        if pyha_settings.first().enableWeeklyMissingHandlersEmail:
            c = MissingHandlersCommand()
            c.handle()
            connection.close()


def decline_overdue_collections():
    pyha_settings = AdminPyhaSettings.objects.filter(settingsName='default')
    if pyha_settings.exists():
        if pyha_settings.first().enableDeclineOverdueCollections:
            c = DeclineOverDueCollectionsCommand()
            c.handle()
            connection.close()


def check_failed_download_requests():
    c = CheckFailedRequestsCommand()
    c.handle()
    connection.close()


def update_statistics():
    c = UpdateStatisticsCacheCommand()
    c.handle()
    connection.close()


def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()


def scheduler():
    schedule.every().monday.at("11:22").do(run_threaded, timed_email)
    schedule.every().thursday.at("11:22").do(run_threaded, timed_email)

    schedule.every().day.at("11:22").do(run_threaded, timed_email_to_requesters)

    schedule.every().tuesday.at("11:22").do(run_threaded, missing_handlers_email)

    schedule.every().day.at("01:44").do(run_threaded, update_statistics)

    schedule.every(30).minutes.do(run_threaded, check_failed_download_requests)

    while True:
        schedule.run_pending()
        sleep(1)


schedule_thread = Thread(target=scheduler)
schedule_thread.daemon = True
schedule_thread.start()
