import os
from unittest import mock

import requests_mock
from django.conf import settings
from django.test import TestCase

from django_datajsonar.indexing.catalog_reader import CatalogReader
from django_datajsonar.indexing.constants import CATALOG_ROOT
from django_datajsonar.models import ReadDataJsonTask, Node
from django_datajsonar.models.config import IndexingConfig
from django_datajsonar.tests.helpers import create_node, open_catalog
from django_datajsonar.utils.catalog_file_generator import CatalogFileGenerator


@mock.patch('django_datajsonar.indexing.catalog_reader.DatabaseLoader')
class CatalogReaderTests(TestCase):
    def test_verify_ssl_sent_to_loader_is_false_by_default(self, database_loader):
        node = create_node('sample_data.json')
        task = ReadDataJsonTask.objects.create()
        CatalogReader().index(node, task)
        self.assertEqual(database_loader.call_args[1]['verify_ssl'], False)

    def test_verify_ssl_is_read_from_config(self, database_loader):
        config = IndexingConfig.get_solo()
        config.verify_ssl = True
        config.save()
        node = create_node('sample_data.json')
        task = ReadDataJsonTask.objects.create()
        CatalogReader().index(node, task)
        self.assertEqual(database_loader.call_args[1]['verify_ssl'], True)

    def test_verify_ssl_also_read_from_node(self, database_loader):
        node = create_node('sample_data.json')
        node.verify_ssl = True
        node.save()
        task = ReadDataJsonTask.objects.create()
        CatalogReader().index(node, task)
        self.assertEqual(database_loader.call_args[1]['verify_ssl'], True)

    def test_catalog_indexation_creates_catalog_files(self, database_loader):
        node = create_node('sample_data.json')
        task = ReadDataJsonTask.objects.create()
        json_file_path = os.path.join(settings.MEDIA_ROOT, CATALOG_ROOT, node.catalog_id, 'data.json')
        xlsx_file_path = os.path.join(settings.MEDIA_ROOT, CATALOG_ROOT, node.catalog_id, 'catalog.xlsx')

        CatalogReader().index(node, task)
        self.assertTrue(os.path.exists(json_file_path))
        self.assertTrue(os.path.exists(xlsx_file_path))

    def test_catalog_url_request_does_not_verify_ssl_by_default(self, _database_loader):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_format='json',
                                   catalog_url='https://fakeurl.com/data.json',
                                   indexable=True)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/data.json', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
            self.assertEqual(2, len(m.request_history))
            for request in m.request_history:
                self.assertTrue(request.verify)

    def test_catalog_url_request_verifies_ssl_according_to_node(self, _database_loader):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_format='json',
                                   catalog_url='https://fakeurl.com/data.json',
                                   indexable=True,
                                   verify_ssl=False)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/data.json', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
            self.assertEqual(2, len(m.request_history))
            for request in m.request_history:
                self.assertFalse(request.verify)

    def test_catalog_url_request_verifies_ssl_on_enabled_node(self, _database_loader):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_format='json',
                                   catalog_url='https://fakeurl.com/data.json',
                                   indexable=True,
                                   verify_ssl=True)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/data.json', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
            self.assertEqual(2, len(m.request_history))
            for request in m.request_history:
                self.assertTrue(request.verify)
