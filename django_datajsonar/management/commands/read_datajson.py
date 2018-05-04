#! coding: utf-8
import logging

from django.core.management import BaseCommand

from django_datajsonar.models import ReadDataJsonTask
from django_datajsonar.tasks import read_datajson

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para ejecutar la indexación manualmente de manera sincrónica,
    útil para debugging. No correr junto con el rqscheduler para asegurar
    la generación de reportes correcta."""

    def add_arguments(self, parser):
        parser.add_argument('--whitelist', action='store_true')

    def handle(self, *args, **options):
        status = [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]
        if ReadDataJsonTask.objects.filter(status__in=status):
            logger.info(u'Ya está corriendo una indexación')
            return

        task = ReadDataJsonTask()
        task.save()

        read_datajson(task, whitelist=options['whitelist'])
