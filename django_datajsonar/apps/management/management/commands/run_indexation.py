#! coding: utf-8
from django.core.management import BaseCommand

from django_datajsonar.apps.management.tasks import schedule_new_read_datajson_task


class Command(BaseCommand):

    def handle(self, *args, **options):
        schedule_new_read_datajson_task()
