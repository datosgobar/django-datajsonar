# -*- coding: utf-8 -*-
from django.utils import timezone
from django_rq import job
from freezegun import freeze_time

from django_datajsonar.forms import SynchroForm

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.conf import settings

from django_datajsonar.models import Synchronizer, Stage, ReadDataJsonTask
from django_datajsonar.synchronizer import start_synchros, upkeep, create_or_update_synchro


@job("default")
def callable_method():
    ReadDataJsonTask.objects.create()


@freeze_time("2019-01-02 00:01:00")
class SynchronizationTests(TestCase):

    @classmethod
    @freeze_time("2019-01-01 00:00:00")
    def setUpTestData(cls):
        previous_stage = None
        for x in range(0, 3):
            new_stage = Stage.objects.create(callable_str='django_datajsonar.tests.synchro_tests.callable_method',
                                             task='django_datajsonar.models.ReadDataJsonTask',
                                             queue='indexing', next_stage=previous_stage, name='stage ' + str(x))
            previous_stage = new_stage
        Synchronizer.objects.create(start_stage=new_stage,
                                    name='test_synchro',
                                    frequency=Synchronizer.DAILY,
                                    scheduled_time=timezone.now())

    def test_create_stage_with_no_name(self):
        with self.assertRaises(ValidationError):
            Stage.objects.create(callable_str='django_datajsonar.tasks.schedule_full_read_task13',
                                 task='django_datajsonar.models.ReadDataJsonTask',
                                 queue='indexing')

    def test_create_stage_with_no_callable(self):
        with self.assertRaises(ValidationError):
            Stage.objects.create(task='django_datajsonar.models.ReadDataJsonTask',
                                 queue='indexing', name='stage fail')

    def test_create_stage_with_uninportable_callable(self):
        with self.assertRaises(ValidationError):
            Stage.objects.create(callable_str='django_datajsonar.tasks',
                                 task='django_datajsonar.models.ReadDataJsonTask',
                                 queue='indexing', name='stage fail')

    def test_create_stage_with_unimportable_task(self):
        with self.assertRaises(ValidationError):
            Stage.objects.create(callable_str='django_datajsonar.tasks.schedule_full_read_task',
                                 task='django_datajsonar.models',
                                 queue='indexing', name='stage fail')

    def test_save_self_referential_stage(self):
        with self.assertRaises(ValidationError):
            stage = Stage.objects.create(callable_str='django_datajsonar.tasks.schedule_full_read_task',
                                         task='django_datajsonar.models.ReadDatajsonTask',
                                         queue='indexing', name='self referential')
            stage.next_stage = stage
            stage.save()

    def test_save_with_bad_queue(self):
        with self.assertRaises(ValidationError):
            Stage.objects.create(callable_str='django_datajsonar.tasks.schedule_full_read_task',
                                 task='django_datajsonar.models.ReadDatajsonTask',
                                 queue='bad_queue', name='stage fail')

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

    @patch('django_datajsonar.tests.synchro_tests.callable_method')
    @patch('django_datajsonar.models.pending_or_running_jobs')
    def test_synchronizator_runs_task(self, mock_queue, mock_method):
        mock_queue.return_value = False
        self.assertEqual(0, mock_method.delay.call_count)
        start_synchros()
        self.assertEqual(1, mock_method.delay.call_count)
        upkeep()
        self.assertEqual(2, mock_method.delay.call_count)

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

    @freeze_time("2019-01-01 10:00:00")
    def test_synchro_wont_run_if_started_too_early(self):
        synchro = Synchronizer.objects.get(name='test_synchro')
        start_synchros()

        # Esperado: no comienza, al correrse todos los días 12 AM, now() < 12 AM de mañana

        self.assertEqual(synchro.status, Synchronizer.STAND_BY)


class DefaultTaskSchedulingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        defaults = [
            {
                'name': 'synchro_1',
                'stages':
                    [
                        {
                            'name': 'stage_1',
                            'callable_str': 'django_datajsonar.tests.synchro_tests.callable_method',
                            'queue': 'default'
                        },
                        {
                            'name': 'stage_2',
                            'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
                            'task': 'django_datajsonar.models.ReadDataJsonTask',
                            'queue': 'indexing'
                        },
                    ]
            },
            {
                'name': 'synchro_2',
                'stages':
                    [
                        {
                            'name': 'stage_3',
                            'callable_str': 'django_datajsonar.tasks.schedule_full_read_task',
                            'task': 'django_datajsonar.models.ReadDataJsonTask',
                            'queue': 'indexing'
                        },
                        {
                            'name': 'stage_4',
                            'callable_str': 'django_datajsonar.tests.synchro_tests.callable_method',
                            'queue': 'default'
                        },
                    ]
            }
        ]
        setattr(settings, 'DEFAULT_PROCESSES', defaults)
        call_command('schedule_default_processes')

    def test_create_stages(self):
        self.assertEqual(4, Stage.objects.all().count())
        self.assertEqual(2, Stage.objects.
                         filter(callable_str='django_datajsonar.tests.synchro_tests.callable_method').count())
        self.assertEqual(2, Stage.objects.filter(task='django_datajsonar.models.ReadDataJsonTask').count())
        self.assertEqual(2, Stage.objects.filter(queue='indexing').count())

    def test_create_synchronizers(self):
        self.assertEqual(2, Synchronizer.objects.all().count())
        self.assertEqual(1, Synchronizer.objects.filter(name='synchro_1').count())
        self.assertEqual(1, Synchronizer.objects.filter(name='synchro_2').count())

    def test_processes_get_updated(self):
        synchro_1 = Synchronizer.objects.get(name='synchro_1')
        synchro_2 = Synchronizer.objects.get(name='synchro_2')
        synchro_1.start_stage = synchro_2.start_stage
        synchro_1.save()
        call_command('schedule_default_processes')
        self.assertEqual(2, Synchronizer.objects.all().count())
        self.assertEqual(4, Stage.objects.all().count())
        synchro_1.refresh_from_db()
        synchro_2.refresh_from_db()
        self.assertNotEqual(synchro_1.start_stage, synchro_2.start_stage)


class SynchronizerUtilsTests(TestCase):

    def test_create_synchro(self):
        self.create_synchro()
        self.assertTrue(Synchronizer.objects.count())

    def test_update_synchro(self):
        synchro = self.create_synchro()
        create_or_update_synchro(synchro.id,
                                 [Stage.objects.first()],
                                 {'name': 'new_name'})

        self.assertEqual(Synchronizer.objects.first().name, 'new_name')

    def test_add_new_stages(self):
        synchro = self.create_synchro()

        stages = synchro.get_stages()
        new_stage = Stage.objects.create(name='new_stage',
                                         queue='default',
                                         callable_str='django_datajsonar.tests.synchro_tests.callable_method')
        stages[0].next_stage = new_stage
        stages[0].save()
        stages.append(new_stage)
        synchro = create_or_update_synchro(synchro.id, stages)

        self.assertEqual(Synchronizer.objects.count(), 1)
        self.assertEqual(len(synchro.get_stages()), 2)

    def test_remove_stages(self):
        stages = []
        next_stage = None
        for i in range(3):
            stage = Stage.objects.create(
                name='Stage {}'.format(i),
                queue='default',
                callable_str='django_datajsonar.tests.synchro_tests.callable_method')
            stage.next_stage = next_stage
            next_stage = stage
            stage.save()
            stages.append(stage)

        stages.reverse()
        synchro = self.create_synchro(stages=stages)

        stages.pop()
        stages[-1].next_stage = None
        stages[-1].save()

        synchro = create_or_update_synchro(synchro.id, stages)
        self.assertEqual(len(synchro.get_stages()), 2)

    @staticmethod
    def create_synchro(stages=None):
        if stages is None:
            stages = [Stage.objects.create(name='a',
                                           queue='default',
                                           callable_str='django_datajsonar.tests.synchro_tests.callable_method')]
        return create_or_update_synchro(None,
                                        stages,
                                        {'name': 'test_name',
                                         'scheduled_time': timezone.now(),
                                         'frequency': Synchronizer.DAILY})
