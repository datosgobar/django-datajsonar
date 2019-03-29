#! coding: utf-8

from __future__ import unicode_literals
from django.conf import settings

from django_datajsonar.utils.utils import import_string, pending_or_running_jobs


def pending_or_running_jobs_in_task_queue(task_model):
    for name, stage_settings in settings.DATAJSONAR_STAGES.items():
        stage_task_model = import_string(stage_settings['task'])
        if stage_task_model == task_model:
            return pending_or_running_jobs(stage_settings['queue'])

    raise ValueError('No hay stage que use el modelo {task_model}'.format(task_model=task_model))
