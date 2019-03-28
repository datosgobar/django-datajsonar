# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import csv
import io

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test.client import Client

from ..models import DatasetIndexingFile
from django_datajsonar.tasks import bulk_whitelist
from django_datajsonar.models import Catalog, Dataset

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class BulkIndexingTests(TestCase):

    test_catalog = 'test'
    other_catalog = 'other'

    catalogs = (test_catalog, other_catalog)
    datasets_per_catalog = 3

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('test_admin', 'myemail@test.com', 'test_pass')
        self.user = User(username='test_user', password='test_pass', email='test@email.com')
        self.user.save()

        for catalog in self.catalogs:
            catalog_model = Catalog(identifier=catalog, title='', metadata='')
            catalog_model.save()
            for i in range(self.datasets_per_catalog):
                dataset = Dataset(identifier=i, catalog=catalog_model, metadata='')
                dataset.save()

    def test_indexing_file(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='1')
        self.assertFalse(dataset.federable)

        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_whitelist(idx_file.id)
        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='1')
        self.assertTrue(dataset.federable)

    def test_dataset_not_in_file_unaffected(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='0')
        self.assertFalse(dataset.federable)
        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_whitelist(idx_file.id)

        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='0')
        self.assertFalse(dataset.federable)

    def test_idx_file_model_changes_states(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')
        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_whitelist(idx_file.id)

        idx_file = DatasetIndexingFile.objects.first()
        self.assertEqual(idx_file.state, idx_file.PROCESSED)

    def test_missing_dataset_header(self):
        filepath = os.path.join(dir_path, 'missing_dataset_headers.csv')
        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_whitelist(idx_file.id)

        idx_file = DatasetIndexingFile.objects.first()
        self.assertEqual(idx_file.state, idx_file.FAILED)

    def test_missing_catalog(self):
        filepath = os.path.join(dir_path, 'test_missing_catalog.csv')
        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()

            bulk_whitelist(idx_file.id)

        idx_file = DatasetIndexingFile.objects.first()
        dataset = Dataset.objects.get(catalog__identifier=self.test_catalog, identifier='1')
        self.assertEqual(idx_file.state, idx_file.PROCESSED)
        self.assertTrue(dataset.federable)

    def test_config_csv_view(self):
        filepath = os.path.join(dir_path, 'test_indexing_file.csv')
        with open(filepath, 'rb') as f:
            idx_file = DatasetIndexingFile(indexing_file=SimpleUploadedFile(filepath, f.read()),
                                           uploader=self.user)
            idx_file.save()
            bulk_whitelist(idx_file.id)

        response = self.client.get(reverse('admin:config_csv'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        config_csv = csv.reader(io.StringIO(content))
        csv_indexables = [row[1] for row in config_csv][1:]
        model_indexables = list(Dataset.objects.filter(federable=True).values_list("identifier", flat=True))
        self.assertListEqual(sorted(csv_indexables), sorted(model_indexables))

    def tearDown(self):
        for catalog in self.catalogs:
            Catalog.objects.get(identifier=catalog).delete()
        self.user.delete()
