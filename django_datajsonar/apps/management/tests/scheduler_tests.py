#!coding=utf8

import datetime
from django.test import TestCase
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
             'default_callable': 'django_datajsonar.libs.indexing.tasks.schedule_new_read_datajson_task',
             'default_interval': 24,
             'default_unit': 'hours'
             },
            {'command': 'schedule_task_finisher',
             'default_callable': 'django_datajsonar.libs.indexing.tasks.close_read_datajson_task',
             'default_interval': 5,
             'default_unit': 'minutes'
             },
        ]

    def test_pass_no_optional_arguments(self):
        for profile in self.profiles:
            args = [profile['command']+'_name']
            opts = {}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command']+'_name',
                                                         callable=profile['default_callable'],
                                                         interval=profile['default_interval'],
                                                         interval_unit=profile['default_unit']))

    def test_pass_time_argument(self):
        for profile in self.profiles:
            args = [profile['command']+'_name']
            opts = {'time': ['12', '45']}
            call_command(profile['command'], *args, **opts)
            start_time = now() + datetime.timedelta(days=1)
            start_time = start_time.replace(hour=12, minute=45, second=0, microsecond=0)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command']+'_name',
                                                         callable=profile['default_callable'],
                                                         scheduled_time=start_time))

    def test_pass_interval_argument(self):
        for profile in self.profiles:
            args = [profile['command']+'_name']
            opts = {'interval': ['300', 'minutes']}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command']+'_name',
                                                         callable=profile['default_callable'],
                                                         interval=300,
                                                         interval_unit='minutes'))


    def test_pass_callable_argument(self):
        for profile in self.profiles:
            args = [profile['command']+'_name']
            method = 'django_datajsonar.apps.management.tests.scheduler_tests.callable_method'
            opts = {'callable': method}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command']+'_name',
                                                         callable=method,
                                                         interval=profile['default_interval'],
                                                         interval_unit=profile['default_unit']))

    def test_update_job(self):
        for profile in self.profiles:
            args = [profile['command']+'_name']
            opts = {}
            call_command(profile['command'], *args, **opts)
            self.assertTrue(RepeatableJob.objects.filter(name=profile['command']+'_name',
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
