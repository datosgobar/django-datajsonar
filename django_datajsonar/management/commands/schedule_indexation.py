#! coding: utf-8
import logging

from django.core.management import BaseCommand
from ._utils import add_common_arguments, handle_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        add_common_arguments(parser)
        parser.set_defaults(callable='django_datajsonar.tasks.schedule_new_read_datajson_task',
                            time=[6, 0],
                            interval=[24, 'hours'])

    def handle(self, *args, **options):
        handle_command(options, logger)
