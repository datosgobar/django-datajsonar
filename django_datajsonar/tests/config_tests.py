# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.core.files.storage import default_storage
from nose.tools import raises

from django_datajsonar.models import Distribution, get_distribution_storage
from datetime import datetime


class DistributionStorageTests(TestCase):

    def test_default_settings(self):
        self.assertEqual(Distribution.data_file.field.storage, default_storage)

    def test_custom_storage(self):
        """Testea el dynamic import del storage. Usamos datetime como un ejemplo
        de clase dentro de un módulo
        """
        with self.settings(DATAJSON_AR_DISTRIBUTION_STORAGE='datetime.datetime'):
            storage = get_distribution_storage()

            self.assertEqual(storage, datetime)

    @raises(ImproperlyConfigured)
    def test_invalid_custom_storage(self):
        """Testea el dynamic import del storage. Usamos datetime como un ejemplo
        de clase dentro de un módulo
        """
        with self.settings(DATAJSON_AR_DISTRIBUTION_STORAGE='django_datajsonar.models.invalid'):
            get_distribution_storage()
