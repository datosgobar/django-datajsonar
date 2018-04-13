#! coding: utf-8
import logging

from django.core.management import BaseCommand
from ._utils import check_for_previously_scheduled_jobs, update_or_create_repeatable_jobs

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging. No correr junto con el rqscheduler para asegurar
    la generación de reportes correcta."""

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='The name for the repeatable job')

        parser.add_argument('-c', '--callable', type=str,
                            help='importable method to be called',
                            default='django_datajsonar.libs.indexing.tasks.schedule_new_read_datajson_task')

        parser.add_argument('-t', '--time', nargs=2,
                            help='UTC hour and minutes to schedule first job, default: 6:00am',
                            metavar=('HOURS', 'MINUTES'),
                            default=[6, 0]
                            )

        parser.add_argument('-i', '--interval', nargs=2,
                            help='interval and unit in which to repeat the job, default: 24 hours',
                            metavar=('UNIT', '[weeks|days|hours|minutes]'),
                            default=[24, 'hours']
                            )

    def handle(self, *args, **options):
        try:
            check_for_previously_scheduled_jobs(options)
        except ValueError as e:
            logger.info('Ya hay un RepeatableJob registrado con ese metodo e intervalo')
            raise e
        update_or_create_repeatable_jobs(options)
