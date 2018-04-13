#! coding: utf-8
from scheduler.models import RepeatableJob


def update_or_create_repeatable_jobs(name, method, start_time, interval):

    RepeatableJob.objects.update_or_create(
        name=name,
        defaults={
            'callable': method,
            'queue': 'indexing',
            'scheduled_time': start_time,
            'interval': int(interval[0]),
            'interval_unit': interval[1],
            'repeat': None
        })


# chequear que no haya un trabajo scheduleado previo con el mismo intervalo y callable
def check_for_previously_scheduled_jobs(method, interval):
    previously_scheduled_jobs = RepeatableJob.objects.filter(callable=method,
                                                             interval=int(interval[0]),
                                                             interval_unit=interval[1])
    if previously_scheduled_jobs:
        raise ValueError('Ya hay un RepeatableJob registrado con ese metodo e intervalo')
