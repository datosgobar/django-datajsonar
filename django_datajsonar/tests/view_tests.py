import json

from django.test import TestCase, Client
from django.urls import reverse

from django_datajsonar.utils.catalog_file_generator import CatalogFileGenerator
from .helpers import create_node, open_catalog


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_xlsx_file_is_served_as_attachment(self):
        node = create_node('catalog.xlsx')
        CatalogFileGenerator(node).generate_files()
        response = self.client.get(reverse("django_datajsonar:xlsx_catalog",
                                           args=['test_catalog']))
        content_disposition = response["Content-Disposition"]
        self.assertIn("attachment;", content_disposition)

    def test_json_file_is_not_served_as_attachment(self):
        node = create_node('another_catalog.json')
        CatalogFileGenerator(node).generate_files()
        response = self.client.get(reverse("django_datajsonar:json_catalog",
                                           args=['test_catalog']))
        content_disposition = response["Content-Disposition"]
        self.assertNotIn("attachment;", content_disposition)

    def test_json_file_content_in_response_content(self):
        node = create_node('another_catalog.json')
        CatalogFileGenerator(node).generate_files()
        response = self.client.get(reverse("django_datajsonar:json_catalog",
                                           args=['test_catalog']))
        response_json = json.loads(response.getvalue().decode('utf-8'))
        with open_catalog('another_catalog.json') as file:
            file_json = json.loads(file.read().decode('utf-8'))
            self.assertEquals(response_json, file_json)
