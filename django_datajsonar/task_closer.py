from django_datajsonar.models import AbstractTask
from django_datajsonar.utils.get_jobs_in_task_queue import pending_or_running_jobs_in_task_queue


class TaskCloser(object):

    def __init__(self, task_jobs=pending_or_running_jobs_in_task_queue):
        self.task_jobs = task_jobs

    def close_all_opened(self, task_model):
        if not self.has_jobs_in_queue(task_model):
            task_model.objects.update(status=AbstractTask.FINISHED)

    def has_jobs_in_queue(self, task_model):
        return self.task_jobs(task_model)
