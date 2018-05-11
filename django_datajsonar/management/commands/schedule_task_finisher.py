#! coding: utf-8
import logging

from django.core.management import BaseCommand
from ._utils import add_common_arguments, handle_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        add_common_arguments(parser)
        parser.set_defaults(callable='django_datajsonar.indexing.tasks.close_read_datajson_task',
                            time=[0, 0],
                            interval=[5, 'minutes'])

    def handle(self, *args, **options):
        handle_command(options, logger)
