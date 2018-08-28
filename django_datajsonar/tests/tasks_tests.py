#!coding=utf8
import os

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from unittest import skipIf

from django_datajsonar.models import Field
from django_datajsonar.tasks import read_datajson, schedule_new_read_datajson_task,\
    schedule_full_read_task, schedule_metadata_read_task
from django_datajsonar.models import ReadDataJsonTask, Node

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')

skip = False
try:
    requests.head('http://infra.datos.gob.ar/catalog/sspm/data.json', timeout=1).raise_for_status()
except requests.exceptions.RequestException:
    skip = True


@skipIf(skip, "Distribuciones remotas caídas")
class ReadDataJsonTest(TestCase):

    def setUp(self):
        self.user = User(username='test', password='test', email='test@test.com', is_staff=True)
        self.user.save()

    def test_read(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()
        task = ReadDataJsonTask()
        task.save()
        read_datajson(task, whitelist=True)
        self.assertTrue(Field.objects.filter(distribution__dataset__catalog__identifier=identifier))

    def test_read_datajson_command(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()
        # Esperado: mismo comportamiento que llamando la función read_datajson
        call_command('read_datajson', whitelist=True)
        self.assertTrue(Field.objects.filter(distribution__dataset__catalog__identifier=identifier))

    def test_read_datajson_while_indexing(self):
        identifier = 'test_id'
        Node(catalog_id=identifier,
             catalog_url=os.path.join(dir_path, 'sample_data.json'),
             indexable=True).save()

        ReadDataJsonTask(status=ReadDataJsonTask.RUNNING).save()

        # Esperado: no se crea una segunda tarea
        call_command('read_datajson')
        self.assertEqual(ReadDataJsonTask.objects.all().count(), 1)


class SchedulingMethodsTest(TestCase):

    def test_read_datajson_task_is_created_without_default_value(self):
        self.assertEqual(0, ReadDataJsonTask.objects.all().count())
        schedule_new_read_datajson_task()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())
        task = ReadDataJsonTask.objects.all().first()
        self.assertEqual(ReadDataJsonTask.COMPLETE_RUN, task.indexing_mode)

    def test_read_datajson_task_is_created_with_default_value(self):
        with self.settings(DATAJSON_AR_DOWNLOAD_RESOURCES=False):
            self.assertEqual(0, ReadDataJsonTask.objects.all().count())
            schedule_new_read_datajson_task()
            self.assertEqual(1, ReadDataJsonTask.objects.all().count())
            task = ReadDataJsonTask.objects.all().first()
            self.assertEqual(ReadDataJsonTask.METADATA_ONLY, task.indexing_mode)

    def test_only_one_running_task_is_allowed(self):
        self.assertEqual(0, ReadDataJsonTask.objects.all().count())
        schedule_new_read_datajson_task()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())

        # Asincrónicamente, las tareas se marcan como terminadas al final de la ejecución.
        # Marco esta como corriendo para salvar eso.
        task = ReadDataJsonTask.objects.all().first()
        task.status = ReadDataJsonTask.RUNNING
        task.save()

        schedule_new_read_datajson_task()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())

    def test_full_run_creates_task_with_correct_attribute(self):
        self.assertEqual(0, ReadDataJsonTask.objects.all().count())
        schedule_full_read_task()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())
        task = ReadDataJsonTask.objects.all().first()
        self.assertEqual(ReadDataJsonTask.COMPLETE_RUN, task.indexing_mode)

    def test_metadata_only_run_creates_task_with_correct_attribute(self):
        self.assertEqual(0, ReadDataJsonTask.objects.all().count())
        schedule_metadata_read_task()
        self.assertEqual(1, ReadDataJsonTask.objects.all().count())
        task = ReadDataJsonTask.objects.all().first()
        self.assertEqual(ReadDataJsonTask.METADATA_ONLY, task.indexing_mode)
