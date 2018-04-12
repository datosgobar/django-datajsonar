#!coding=utf8

import datetime
from StringIO import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.utils.timezone import now
from scheduler.models import RepeatableJob


def callable_method():
    pass


class ReadDataJsonTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.default_callable = 'django_datajsonar.libs.indexing.tasks.schedule_new_read_datajson_task'
        cls.default_interval = 24
        cls.default_unit = 'hours'

    def test_pass_no_optional_arguments(self):
        args = ['aName']
        opts = {}
        call_command('schedule_indexation', *args, **opts)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=self.default_callable,
                                                     interval=self.default_interval,
                                                     interval_unit=self.default_unit))

    def test_pass_time_argument(self):
        args = ['aName']
        opts = {'time': ['12', '45']}
        call_command('schedule_indexation', *args, **opts)
        start_time = now() + datetime.timedelta(days=1)
        start_time = start_time.replace(hour=12, minute=45, second=0, microsecond=0)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=self.default_callable,
                                                     scheduled_time=start_time))

    def test_pass_interval_argument(self):
        args = ['aName']
        opts = {'interval': ['300', 'minutes']}
        call_command('schedule_indexation', *args, **opts)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=self.default_callable,
                                                     interval=300,
                                                     interval_unit='minutes'))

    def test_pass_callable_argument(self):
        args = ['aName']
        method = 'django_datajsonar.apps.management.tests.scheduler_tests.callable_method'
        opts = {'callable': method}
        call_command('schedule_indexation', *args, **opts)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=method))

    def test_update_job(self):
        args = ['aName']
        opts = {}
        call_command('schedule_indexation', *args, **opts)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=self.default_callable,
                                                     interval=self.default_interval,
                                                     interval_unit=self.default_unit))
        opts = {'interval': ['2', 'days']}
        call_command('schedule_indexation', *args, **opts)
        self.assertTrue(RepeatableJob.objects.filter(name='aName',
                                                     callable=self.default_callable,
                                                     interval=2,
                                                     interval_unit='days'))

        self.assertFalse(RepeatableJob.objects.filter(name='aName',
                                                      callable=self.default_callable,
                                                      interval=self.default_interval,
                                                      interval_unit=self.default_unit))

    def test_notify_repeated_jobs(self):
        args = ['aName']
        opts = {}
        call_command('schedule_indexation', *args, **opts)

        args = ['otherName']
        opts = {}
        out = StringIO()
        call_command('schedule_indexation', stdout=out, *args, **opts)
        self.assertIn('Ya hay un RepeatableJob registrado con ese metodo e intervalo',
                      out.getvalue())