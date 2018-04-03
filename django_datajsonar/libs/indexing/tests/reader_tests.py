#! coding: utf-8
import os

from django.test import TestCase

from django_datajsonar.apps.api.models import Distribution, Field
from django_datajsonar.apps.management.models import ReadDataJsonTask, Node
from django_datajsonar.libs.indexing.catalog_reader import index_catalog

SAMPLES_DIR = os.path.join('django_datajsonar', 'libs', 'indexing', 'tests', 'samples')
CATALOG_ID = 'test_catalog'


class ReaderTests(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'full_ts_data.json')
    catalog_id = 'catalog_id'

    def setUp(self):
        self.task = ReadDataJsonTask.objects.create()
        self.node = Node(catalog_id=self.catalog_id, catalog_url=self.catalog, indexable=True)
        self.node.save()

    def test_index_same_series_different_catalogs(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        count = Field.objects.filter(metadata__contains='212.1_PSCIOS_ERN_0_0_25').count()

        self.assertEqual(count, 1)

    def test_dont_index_same_distribution_twice(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribucion es marcada como no indexable hasta que cambien sus datos
        self.assertFalse(distribution.indexable)

    def test_first_time_distribution_indexable(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        self.assertTrue(distribution.indexable)

    def test_index_same_distribution_if_data_changed(self):
        index_catalog(self.node, self.task, read_local=True, whitelist=True)
        new_catalog = os.path.join(SAMPLES_DIR, 'full_ts_data_changed.json')
        self.node.catalog_url = new_catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        distribution = Distribution.objects.get(identifier='212.1')

        # La distribución fue indexada nuevamente, está marcada como indexable
        self.assertTrue(distribution.indexable)

    def test_error_distribution_logs(self):
        catalog = os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json')
        self.node.catalog_url = catalog
        self.node.save()
        index_catalog(self.node, self.task, read_local=True, whitelist=True)

        self.assertGreater(len(ReadDataJsonTask.objects.get(id=self.task.id).logs), 10)