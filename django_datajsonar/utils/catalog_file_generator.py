import os
import requests
from django.core.files import File

from pydatajson import DataJson
from pydatajson.writers import write_xlsx_catalog, write_json_catalog
from conf.settings.base import MEDIA_ROOT
from django_datajsonar.models import Node


class CatalogFileGenerator:
    def __init__(self, node):
        self.node = node
        self.xlsx_catalog_dir = os.path.join(MEDIA_ROOT, 'catalog', self.node.catalog_id, 'catalog.xlsx')
        self.json_catalog_dir = os.path.join(MEDIA_ROOT, 'catalog', self.node.catalog_id, 'data.json')

    def generate_files(self):
        format = self.node.catalog_format

        catalog = DataJson(self.node.catalog_url)
        catalog_url = self.node.catalog_url

        if format == Node.JSON:
            self._save_json_file_from_catalog(catalog)
            self._generate_xlsx_file_into_model(catalog)
        if format == Node.XLSX:
            self._save_xlsx_file_from_url(catalog_url)
            self._generate_json_file_into_model(catalog)
        else:
            self._generate_json_file_into_model(catalog)
            self._generate_xlsx_file_into_model(catalog)

    def _save_json_file_from_catalog(self, catalog):
        self.node.json_catalog_file.save('data.json', catalog)

    def _save_xlsx_file_from_url(self, url):
        response = requests.get(url)
        response.raise_for_status()
        file_content = response.content

        self.node.xlsx_catalog_file('catalog.xlsx', file_content)

    def _generate_json_file_into_model(self, catalog):
        write_json_catalog(catalog, self.json_catalog_dir)
        self._save_generated_file_to_model(self.json_catalog_dir, 'data.json')

    def _generate_xlsx_file_into_model(self, catalog):
        write_xlsx_catalog(catalog, self.xlsx_catalog_dir)
        self._save_generated_file_to_model(self.xlsx_catalog_dir, 'catalog.xlsx')

    def _save_generated_file_to_model(self, file_dir, new_file_name):
        with open(file_dir, 'rb') as file:
            self.node.json_catalog_file.save(new_file_name, File(file))
