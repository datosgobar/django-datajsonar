import json
import os
import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

from pydatajson import DataJson
from pydatajson.writers import write_xlsx_catalog, write_json_catalog

from django_datajsonar.models import Node


class CatalogFileGenerator:
    def __init__(self, node):
        self.node = node
        self.xlsx_catalog_dir = os.path.join(settings.MEDIA_ROOT, 'catalog', self.node.catalog_id, 'catalog.xlsx')
        self.json_catalog_dir = os.path.join(settings.MEDIA_ROOT, 'catalog', self.node.catalog_id, 'data.json')

    def generate_files(self):
        catalog_format = self.node.catalog_format
        catalog_url = self.node.catalog_url

        catalog = DataJson(catalog_url, catalog_format=catalog_format,
                           verify_ssl=self.node.verify_ssl)

        if catalog_format == Node.JSON:
            self._save_json_file_from_url(catalog_url)
            self._generate_xlsx_file_into_model(catalog)
        elif catalog_format == Node.XLSX:
            self._save_xlsx_file_from_url(catalog_url)
            self._generate_json_file_into_model(catalog)
        else:
            self._generate_json_file_into_model(catalog)
            self._generate_xlsx_file_into_model(catalog)

    def _save_json_file_from_url(self, url):
        file_content = self._get_catalog_content_from_url(url).decode('utf-8')
        self.node.json_catalog_file.save('data.json', ContentFile(file_content))

    def _save_xlsx_file_from_url(self, url):
        file_content = self._get_catalog_content_from_url(url)
        self.node.xlsx_catalog_file.save('catalog.xlsx', ContentFile(file_content))

    def _get_catalog_content_from_url(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def _generate_json_file_into_model(self, catalog):
        write_json_catalog(catalog, self.json_catalog_dir)
        self._save_generated_file_to_model(self.json_catalog_dir, 'data.json')

    def _generate_xlsx_file_into_model(self, catalog):
        write_xlsx_catalog(catalog, self.xlsx_catalog_dir)
        self._save_generated_file_to_model(self.xlsx_catalog_dir, 'catalog.xlsx')

    def _save_generated_file_to_model(self, file_dir, new_file_name):
        file_field = self.node.json_catalog_file if new_file_name == 'data.json' \
            else self.node.xlsx_catalog_file
        with open(file_dir, 'rb') as file:
            file_field.save(new_file_name, File(file))
