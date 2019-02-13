# coding=utf-8
from __future__ import unicode_literals
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduler.models import RepeatableJob

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Asegura la existencia de un upkeep job programado para el
    funcionamiento de los procesos de alto nivel"""

    def handle(self, *args, **options):
        # Llama sincrónicamente
        job, created = RepeatableJob.objects.get_or_create(
            callable='django_datajsonar.synchronizer.upkeep',
            defaults={
                'name': 'Synchronizer upkeep job',
                'queue': 'default',
                'scheduled_time': timezone.now(),
                'interval_unit': 'minutes',
                'interval': 1,
                'repeat': None
            }
        )
        if not job.is_scheduled():
            job.schedule()

        logger.info('created: %s', str(created))
        logger.info('name: %s', job.name)
        logger.info('scheduled: %s', str(job.is_scheduled()))
