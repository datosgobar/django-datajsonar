from django_datajsonar.models import AbstractTask
from django_datajsonar.utils import pending_or_running_jobs


class TaskCloser(object):

    def __init__(self, task_model, does_queue_have_running_jobs=pending_or_running_jobs):
        self.does_queue_have_running_jobs = does_queue_have_running_jobs
        self.task_model = task_model

    def close_all_opened(self):
        if not self.does_queue_have_running_jobs('a_queue'):
            self.task_model.objects.update(status=AbstractTask.FINISHED)
