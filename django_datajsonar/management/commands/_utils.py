#! coding: utf-8
import datetime

from django.utils.timezone import localtime
from scheduler.models import RepeatableJob


def add_common_arguments(parser):
    parser.add_argument('name', type=str, help='The name for the repeatable job')
    parser.add_argument(
        '-c', '--callable', type=str,
        help='importable method to be called',
    )
    parser.add_argument(
        '-t', '--time', nargs=2,
        help='UTC hour and minutes to schedule first job',
        metavar=('HOURS', 'MINUTES'),
    )
    parser.add_argument(
        '-i', '--interval', nargs=2,
        help='interval and unit in which to repeat the job',
        metavar=('UNIT', '[weeks|days|hours|minutes]'),
    )


def handle_command(options, logger):
    method = options['callable']
    interval = options['interval']
    try:
        check_for_previously_scheduled_jobs(method, interval)
    except ValueError as e:
        logger.info('Ya hay un RepeatableJob registrado con ese metodo e intervalo')
        raise e

    name = options['name']
    start_time = localtime() + datetime.timedelta(days=1)
    time = [int(component) for component in options['time']]
    start_time = start_time.replace(hour=time[0],
                                    minute=time[1],
                                    second=0,
                                    microsecond=0)
    update_or_create_repeatable_jobs(name, method, start_time, interval)


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
