import os
from unittest.mock import patch

import requests_mock
from django.conf import settings
from django.test import TestCase

from django_datajsonar.indexing.constants import CATALOG_ROOT
from django_datajsonar.models import Node
from django_datajsonar.tests.helpers import create_node, open_catalog
from django_datajsonar.utils.catalog_file_generator import CatalogFileGenerator


class CatalogFileGeneratorTests(TestCase):
    def test_creates_files_in_json_and_xlsx(self):
        node = create_node('sample_data.json')
        file_generator = CatalogFileGenerator(node)
        file_generator.generate_files()
        json_file_path = os.path.join(settings.MEDIA_ROOT, CATALOG_ROOT,
                                      node.catalog_id, 'data.json')
        xlsx_file_path = os.path.join(settings.MEDIA_ROOT, CATALOG_ROOT,
                                      node.catalog_id, 'catalog.xlsx')
        self.assertTrue(os.path.exists(json_file_path))
        self.assertTrue(os.path.exists(xlsx_file_path))

    @patch('django_datajsonar.utils.catalog_file_generator.CatalogFileGenerator._generate_xlsx_file_into_model')
    def test_creates_new_xlsx_file_if_node_format_is_json(self, mock):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_url='https://fakeurl.com/data.json',
                                   catalog_format='json',
                                   indexable=True)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/data.json', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
        mock.assert_called_once()

    @patch('django_datajsonar.utils.catalog_file_generator.CatalogFileGenerator._generate_json_file_into_model')
    def test_creates_new_json_file_if_node_format_is_xlsx(self, mock):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_url='https://fakeurl.com/catalog.xlsx',
                                   catalog_format='xlsx',
                                   indexable=True)
        with open_catalog('catalog.xlsx') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/catalog.xlsx', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
        mock.assert_called_once()

    @patch('django_datajsonar.utils.catalog_file_generator.CatalogFileGenerator._generate_xlsx_file_into_model')
    @patch('django_datajsonar.utils.catalog_file_generator.CatalogFileGenerator._generate_json_file_into_model')
    def test_creates_new_json_and_xlsx_files_if_node_format_unspecified(self, json_gen_mock, xlsx_gen_mock):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_url='https://fakeurl.com/data.json',
                                   indexable=True)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/data.json', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
        json_gen_mock.assert_called_once()
        xlsx_gen_mock.assert_called_once()

    @patch('django_datajsonar.utils.catalog_file_generator.DataJson')
    def test_creates_datajson_with_arguments_specified_in_node(self, datajson_mock):
        node = Node.objects.create(catalog_id='test_catalog',
                                   catalog_format='json',
                                   catalog_url='https://fakeurl.com/without_format',
                                   indexable=True,
                                   verify_ssl=True)
        with open_catalog('sample_data.json') as sample:
            text = sample.read()
        with requests_mock.Mocker() as m:
            m.get('https://fakeurl.com/without_format', status_code=200, content=text)
            CatalogFileGenerator(node).generate_files()
        datajson_mock.assert_called_once_with(node.catalog_url, catalog_format='json',
                                              verify_ssl=True)
