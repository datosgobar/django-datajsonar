#! coding: utf-8
from django_rq import get_queue
from django_datajsonar.models import ReadDataJsonTask


# Para correr con el scheduler
def close_read_datajson_task():
    task = ReadDataJsonTask.objects.last()
    if task.status == task.FINISHED:
        return

    if not get_queue('indexing').jobs:
        task.status = task.FINISHED
        task.save()


