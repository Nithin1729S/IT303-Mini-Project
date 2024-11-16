from celery import shared_task
from mtechMinorEval.models import ActivityLog

@shared_task
def log_activity(activity):
    ActivityLog.objects.create(activity=activity)
