#!coding=utf8

import datetime
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.utils.timezone import now

from scheduler.models import RepeatableJob


def callable_method():
    pass


class ReadDataJsonTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.profiles = [
            {'command': 'schedule_indexation',
             'default_callable': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
             'default_interval': 24,
             'default_unit': 'hours'
             },
            {'command': 'schedule_task_finisher',
             'default_callable': 'django_datajsonar.indexing.tasks.close_read_datajson_task',
             'default_interval': 5,
             'default_unit': 'minutes'
             },
        ]

    def test_pass_no_optional_arguments(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            opts = {}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=profile['default_callable'],
                                                         interval=profile['default_interval'],
                                                         interval_unit=profile['default_unit']))

    def test_pass_time_argument(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            opts = {'time': ['12', '45']}
            call_command(profile['command'], *args, **opts)
            start_time = now() + datetime.timedelta(days=1)
            start_time = start_time.replace(hour=12, minute=45, second=0, microsecond=0)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=profile['default_callable'],
                                                         scheduled_time=start_time))

    def test_pass_interval_argument(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            opts = {'interval': ['300', 'minutes']}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=profile['default_callable'],
                                                         interval=300,
                                                         interval_unit='minutes'))

    def test_pass_callable_argument(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            method = 'django_datajsonar.tests.scheduler_tests.callable_method'
            opts = {'callable': method}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=method,
                                                         interval=profile['default_interval'],
                                                         interval_unit=profile['default_unit']))

    def test_update_job(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            opts = {}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=profile['default_callable'],
                                                         interval=profile['default_interval'],
                                                         interval_unit=profile['default_unit']))

            opts = {'interval': ['2', 'days']}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                         callable=profile['default_callable'],
                                                         interval=2,
                                                         interval_unit='days'))
            self.assertFalse(RepeatableJob.objects.filter(name=profile['command'] + '_name',
                                                          callable=profile['default_callable'],
                                                          interval=profile['default_interval'],
                                                          interval_unit=profile['default_unit']))

    def test_notify_repeated_jobs(self):
        for profile in self.profiles:
            args = [profile['command'] + '_name']
            opts = {}
            call_command(profile['command'], *args, **opts)

            args = [profile['command'] + '_other_name']
            with self.assertRaises(ValueError):
                call_command(profile['command'], *args, **opts)


class DefaultTaskSchedulingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        defaults = [
            {
                'name': 'Read Datajson Task',
                'callable': 'django_datajsonar.tasks.schedule_new_read_datajson_task',
                'start_hour': 3,
                'start_minute': 0,
                'interval': 6,
                'interval_unit': 'hours'
            },
            {
                'name': 'Close Indexing Task',
                'callable': 'django_datajsonar.indexing.tasks.close_read_datajson_task',
                'start_hour': 4,
                'start_minute': 15,
                'interval': 30,
                'interval_unit': 'minutes'
            }
        ]
        setattr(settings, 'DEFAULT_TASKS', defaults)
        call_command('schedule_default_tasks')

    def test_schedule_jobs(self):
        self.assertEqual(2, RepeatableJob.objects.all().count())
        self.assertEqual(1, RepeatableJob.objects.filter(name='Read Datajson Task').count())
        self.assertEqual(1, RepeatableJob.objects.filter(name='Close Indexing Task').count())

    def test_scheduled_intervals(self):
        self.assertEqual(6, RepeatableJob.objects.get(name='Read Datajson Task').interval)
        self.assertEqual('hours', RepeatableJob.objects.get(name='Read Datajson Task').interval_unit)
        self.assertEqual(30, RepeatableJob.objects.get(name='Close Indexing Task').interval)
        self.assertEqual('minutes', RepeatableJob.objects.get(name='Close Indexing Task').interval_unit)

    def test_scheduled_callable(self):
        self.assertEqual('django_datajsonar.tasks.schedule_new_read_datajson_task',
                         RepeatableJob.objects.get(name='Read Datajson Task').callable)
        self.assertEqual('django_datajsonar.indexing.tasks.close_read_datajson_task',
                         RepeatableJob.objects.get(name='Close Indexing Task').callable)

    def test_start_times(self):
        start_time = now() + datetime.timedelta(days=1)
        start_time = start_time.replace(hour=3, minute=0, second=0, microsecond=0)
        self.assertEqual(start_time,
                         RepeatableJob.objects.get(name='Read Datajson Task').scheduled_time)

        start_time = start_time.replace(hour=4, minute=15, second=0, microsecond=0)
        self.assertEqual(start_time,
                         RepeatableJob.objects.get(name='Close Indexing Task').scheduled_time)

    def test_jobs_get_updated(self):
        new_defaults = [
            {
                'name': 'Read Datajson Task',
                'callable': 'django_datajsonar.tests.scheduler_tests.callable_method',
                'start_hour': 5,
                'start_minute': 30,
                'interval': 3,
                'interval_unit': 'days'
            },
        ]
        setattr(settings, 'DEFAULT_TASKS', new_defaults)
        call_command('schedule_default_tasks')
        self.assertEqual(2, RepeatableJob.objects.all().count())
        self.assertEqual('django_datajsonar.tests.scheduler_tests.callable_method',
                         RepeatableJob.objects.get(name='Read Datajson Task').callable)
