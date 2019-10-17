import os

from pydatajson.writers import write_xlsx_catalog, write_json_catalog
from conf.settings.base import MEDIA_ROOT
from django_datajsonar.models import Node


class CatalogFileGenerator:
    def generate_files(self, catalog, node):
        format = node.catalog_format
        catalogs_dir = os.path.join(MEDIA_ROOT, 'catalog', node.catalog_id)

        if format == Node.JSON:
            file_dir = os.path.join(catalogs_dir, 'catalog.xlsx')
            write_xlsx_catalog(catalog, file_dir)
        if format == Node.XLSX:
            file_dir = os.path.join(catalogs_dir, 'data.json')
            write_json_catalog(catalog, file_dir)
        else:
            file_dir = os.path.join(catalogs_dir, 'data.json')
            write_json_catalog(catalog, file_dir)
            file_dir = os.path.join(catalogs_dir, 'catalog.xlsx')
            write_xlsx_catalog(catalog, file_dir)

