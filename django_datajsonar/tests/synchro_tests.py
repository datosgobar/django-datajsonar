# -*- coding: utf-8 -*-

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from django.test import TestCase

from django_datajsonar.models import Synchronizer, Stage, ReadDataJsonTask
from django_datajsonar.synchronizer_tasks import start_synchros, upkeep


class SynchronizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create stages
        previous_stage = None
        for x in range(0, 3):
            new_stage = Stage.objects.create(callable_str='django_datajsonar.tasks.schedule_new_read_datajson_task',
                                             queue='indexing', next_stage=previous_stage)
            previous_stage = new_stage
        Synchronizer.objects.create(start_stage=new_stage, name='test_synchro')

    def test_synchronizator_starts_correctly(self):
        synchro = Synchronizer.objects.get(name='test_synchro')
        self.assertEqual(Synchronizer.STAND_BY, synchro.status)
        start_synchros()
        synchro.refresh_from_db()
        self.assertEqual(Synchronizer.RUNNING, synchro.status)

    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_advance_stage_if_queue_is_empty(self, mock_queue):
        mock_queue.return_value = False
        synchro = Synchronizer.objects.get(name='test_synchro')
        self.assertIsNone(synchro.actual_stage)
        start_synchros()
        synchro.refresh_from_db()
        self.assertEqual(synchro.actual_stage, synchro.start_stage)
        upkeep()
        synchro.refresh_from_db()
        self.assertEqual(synchro.actual_stage, synchro.start_stage.next_stage)

    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_complete_stage_before_advancing(self, mock_queue):
        mock_queue.jobs.return_value = True
        synchro = Synchronizer.objects.get(name='test_synchro')
        self.assertIsNone(synchro.actual_stage)
        start_synchros()
        synchro.refresh_from_db()
        self.assertEqual(synchro.actual_stage, synchro.start_stage)
        upkeep()
        synchro.refresh_from_db()
        self.assertEqual(synchro.actual_stage, synchro.start_stage)
        upkeep()
        synchro.refresh_from_db()
        self.assertEqual(synchro.actual_stage, synchro.start_stage)

    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_synchronizator_runs_task(self, mock_queue):
        mock_queue.return_value = False
        self.assertEqual(0, ReadDataJsonTask.objects.all().count())
        start_synchros()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())
        upkeep()
        self.assertEqual(2, ReadDataJsonTask.objects.all().count())

    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_synchronizator_finishes_correctly(self, mock_queue):
        mock_queue.return_value = False
        synchro = Synchronizer.objects.get(name='test_synchro')
        start_synchros()
        for x in range(0, 3):
            upkeep()
        synchro.refresh_from_db()
        self.assertEqual(Synchronizer.STAND_BY, synchro.status)
        self.assertIsNone(synchro.actual_stage)

    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_stage_closes_task_when_finished(self, mock_queue):
        mock_queue.return_value = False
        start_synchros()
        for x in range(0, 3):
            upkeep()
        self.assertEqual(3, ReadDataJsonTask.objects.filter(status=ReadDataJsonTask.FINISHED).count())
