from django_datajsonar.models import AbstractTask


class TaskCloser(object):

    def __init__(self, task_model):
        self.task_model = task_model

    def close_all_opened(self):
        self.task_model.objects.update(status=AbstractTask.FINISHED)
