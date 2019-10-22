import os

from django_datajsonar.models import Node

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


def create_node(catalog_file_name, catalog_id='test_catalog'):
    return Node.objects.create(catalog_id=catalog_id,
                               catalog_url=os.path.join(SAMPLES_DIR, catalog_file_name),
                               indexable=True)


def catalog_path(file_name):
    return os.path.join(SAMPLES_DIR, file_name)


def open_catalog(file_name):
    return open(catalog_path(file_name), 'rb')
