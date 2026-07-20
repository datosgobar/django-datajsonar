#! coding: utf-8
from django_rq import job
from django_datajsonar.models import ReadDataJsonTask


@job('indexing')
def close_read_datajson_task():
    task = ReadDataJsonTask.objects.last()
    if task and task.status != task.FINISHED:
        task.status = task.FINISHED
        task.save()
