#! coding: utf-8
import logging
import datetime

from scheduler.models import RepeatableJob
from django.core.management import BaseCommand
from django.utils.timezone import now


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging. No correr junto con el rqscheduler para asegurar
    la generación de reportes correcta."""

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='The name for the repeatable job')
        parser.add_argument('-c', '--callable', type=str, help='importable method to be called')
        parser.add_argument('-t', '--time', nargs=2, help='UTC hour and minutes to schedule first job, default: 6:00am')
        parser.add_argument('-i', '--interval', nargs=2,
                            help='interval and unit in which to repeat the job, default: 24 hours')

    def handle(self, *args, **options):
        # chequear que no haya un trabajo scheduleado previo
        method = options['callable'] or 'django_datajsonar.libs.indexing.tasks.schedule_new_read_datajson_task'
        interval = options['interval'] or (24, 'hours')
        previously_scheduled_jobs = RepeatableJob.objects.filter(callable=method,
                                                                 interval=int(interval[0]),
                                                                 interval_unit=interval[1])
        if previously_scheduled_jobs:
            print 'Ya hay un RepeatableJob registrado con ese metodo e intervalo'
            return

        start_time = now() + datetime.timedelta(days=1)
        time = options['time'] or (6, 0)
        start_time = start_time.replace(hour=int(time[0]),
                                        minute=int(time[1]),
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

