from django.conf import settings
from django_rq import get_queue

from django_datajsonar.utils.utils import get_qualified_name


def get_jobs_in_task_queue(task_model):
    for name, stage_settings in settings.DATAJSONAR_STAGES.items():
        qualified_name = get_qualified_name(task_model)
        if stage_settings['task'] == qualified_name:
            return get_queue(stage_settings['queue']).jobs

    raise ValueError('No hay stage que use el modelo {task_model}'.format(task_model=task_model))
