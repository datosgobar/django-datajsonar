#! coding: utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.test import TestCase
from mock import patch

from django_datajsonar.models import ReadDataJsonTask
from django_datajsonar.utils.get_jobs_in_task_queue import get_jobs_in_task_queue
from django_datajsonar.utils.utils import get_qualified_name


@patch('django_datajsonar.utils.get_jobs_in_task_queue.get_queue')
class GetJobsInTaskQueueTests(TestCase):

    def test_get_jobs_for_running_task(self, get_queue):
        task = ReadDataJsonTask
        setattr(settings, 'DATAJSONAR_STAGES', {
            'stage_name': {
                'task': get_qualified_name(task),
                'queue': 'some_queue',
            }
        })

        get_queue().jobs.return_value = ['one_job']

        jobs = get_jobs_in_task_queue(task)
        self.assertEqual(jobs, get_queue().jobs)

    def test_get_jobs_no_associated_queue(self, *_):
        task = ReadDataJsonTask
        setattr(settings, 'DATAJSONAR_STAGES', {})
        with self.assertRaises(ValueError):
            get_jobs_in_task_queue(task)
