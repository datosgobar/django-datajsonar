#! coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.test import TestCase
from mock import patch

from django_datajsonar.synchronizer import close_opened_tasks
from django_datajsonar.utils.utils import import_string


@patch('django_datajsonar.synchronizer.TaskCloser')
class CloseAllTasksTests(TestCase):

    def test_close_all_called_once_per_stage(self, task_closer):
        setattr(settings, 'DATAJSONAR_STAGES', {
            'Read Datajson (complete)': {
                'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
                'queue': 'indexing',
                'task': 'django_datajsonar.models.ReadDataJsonTask',
            },
            'Read Datajson (metadata only)': {
                'callable_str': 'django_datajsonar.tasks.schedule_metadata_read_task',
                'queue': 'indexing',
                'task': 'django_datajsonar.models.ReadDataJsonTask',
            },
        })
        close_opened_tasks()

        self.assertEqual(task_closer().close_all_opened.call_count, 2)

    def test_close_all_no_stages_not_called(self, task_closer):
        setattr(settings, 'DATAJSONAR_STAGES', {})
        close_opened_tasks()
        self.assertEqual(task_closer().close_all_opened.call_count, 0)

    def test_close_all_is_called_with_task(self, task_closer):
        setattr(settings, 'DATAJSONAR_STAGES', {
            'Read Datajson (complete)': {
                'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
                'queue': 'indexing',
                'task': 'django_datajsonar.models.ReadDataJsonTask',
            }
        })
        close_opened_tasks()
        model = import_string('django_datajsonar.models.ReadDataJsonTask')
        task_closer().close_all_opened.assert_called_with(model)
