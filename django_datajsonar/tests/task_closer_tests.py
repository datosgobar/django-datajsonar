from unittest.mock import Mock

from django.test import TestCase

from django_datajsonar.models import AbstractTask
from django_datajsonar.task_closer import TaskCloser


class TaskCloserTests(TestCase):

    def test_close_all_updates_all_models(self):

        mock_task = Mock()
        TaskCloser(mock_task).close_all_opened()

        mock_task.objects.update.assert_called_with(status=AbstractTask.FINISHED)
