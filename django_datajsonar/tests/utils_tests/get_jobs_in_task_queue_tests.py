#! coding: utf-8

from __future__ import unicode_literals

from mock import patch
from django.conf import settings
from django.test import TestCase

from django_datajsonar.models import ReadDataJsonTask
from django_datajsonar.utils.get_jobs_in_task_queue import pending_or_running_jobs_in_task_queue
from django_datajsonar.utils.utils import get_qualified_name


@patch('django_datajsonar.utils.get_jobs_in_task_queue.pending_or_running_jobs')
class GetJobsInTaskQueueTests(TestCase):

    def test_get_jobs_for_running_task(self, pending_or_running_jobs):
        task = ReadDataJsonTask
        setattr(settings, 'DATAJSONAR_STAGES', {
            'stage_name': {
                'task': get_qualified_name(task),
                'queue': 'some_queue',
            }
        })

        pending_or_running_jobs.return_value = True

        jobs = pending_or_running_jobs_in_task_queue(task)
        self.assertTrue(jobs)

    def test_get_jobs_no_associated_queue(self, *_):
        task = ReadDataJsonTask
        setattr(settings, 'DATAJSONAR_STAGES', {})
        with self.assertRaises(ValueError):
            pending_or_running_jobs_in_task_queue(task)
