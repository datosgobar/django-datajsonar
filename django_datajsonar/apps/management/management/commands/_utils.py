#! coding: utf-8
import datetime

from django.utils.timezone import now
from scheduler.models import RepeatableJob


def update_or_create_repeatable_jobs(options):
    method = options['callable']
    interval = options['interval']
    start_time = now() + datetime.timedelta(days=1)
    time = map(int, options['time'])
    start_time = start_time.replace(hour=time[0],
                                    minute=time[1],
                                    second=0,
                                    microsecond=0)

    RepeatableJob.objects.update_or_create(
        name=options['name'],
        defaults={
            'callable': method,
            'queue': 'indexing',
            'scheduled_time': start_time,
            'interval': int(interval[0]),
            'interval_unit': interval[1],
            'repeat': None
        })


# chequear que no haya un trabajo scheduleado previo con el mismo intervalo y callable
def check_for_previously_scheduled_jobs(options):
    method = options['callable']
    interval = options['interval']
    previously_scheduled_jobs = RepeatableJob.objects.filter(callable=method,
                                                             interval=int(interval[0]),
                                                             interval_unit=interval[1])
    if previously_scheduled_jobs:
        raise ValueError('Ya hay un RepeatableJob registrado con ese metodo e intervalo')
