from django.conf import settings
from django_rq import get_queue

from django_datajsonar.utils.utils import import_string


def get_jobs_in_task_queue(task_model):
    for name, stage_settings in settings.DATAJSONAR_STAGES.items():
        stage_task_model = import_string(stage_settings['task'])
        if stage_task_model == task_model:
            return get_queue(stage_settings['queue']).jobs

    raise ValueError('No hay stage que use el modelo {task_model}'.format(task_model=task_model))
