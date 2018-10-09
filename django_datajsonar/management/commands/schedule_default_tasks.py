#! coding: utf-8
import datetime

from django.core.management import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from scheduler.models import RepeatableJob


class Command(BaseCommand):

    def handle(self, *args, **options):
        tasks = getattr(settings, 'DEFAULT_TASKS', [])
        for task in tasks:
            start_time = now() + datetime.timedelta(days=1)
            start_time = start_time.replace(hour=task['start_hour'],
                                            minute=task['start_minute'],
                                            second=0,
                                            microsecond=0)
            RepeatableJob.objects.update_or_create(
                name=task['name'],
                defaults={
                    'callable': task['callable'],
                    'queue': 'indexing',
                    'scheduled_time': start_time,
                    'interval': task['interval'],
                    'interval_unit': task['interval_unit'],
                    'repeat': None
                })
