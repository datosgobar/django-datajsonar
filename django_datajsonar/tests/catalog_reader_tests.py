import os
from unittest import mock

from django.test import TestCase

from conf.settings.base import MEDIA_ROOT
from django_datajsonar.indexing.catalog_reader import CatalogReader
from django_datajsonar.indexing.constants import CATALOG_ROOT
from django_datajsonar.models import Node, ReadDataJsonTask
from django_datajsonar.models.config import IndexingConfig
from django_datajsonar.tests.helpers import create_node


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
        json_file_path = os.path.join(MEDIA_ROOT, CATALOG_ROOT, node.catalog_id, 'data.json')
        xlsx_file_path = os.path.join(MEDIA_ROOT, CATALOG_ROOT, node.catalog_id, 'catalog.xlsx')

        CatalogReader().index(node, task)
        self.assertTrue(os.path.exists(json_file_path))
        self.assertTrue(os.path.exists(xlsx_file_path))
