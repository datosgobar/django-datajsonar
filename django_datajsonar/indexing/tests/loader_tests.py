#! coding: utf-8
import json
import os

from django.conf import settings
from django.test import TestCase
from pydatajson import DataJson

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


from django_datajsonar.models import Catalog, Dataset, Distribution, Field
from django_datajsonar.models import ReadDataJsonTask, Node
from django_datajsonar.indexing.database_loader import DatabaseLoader
from .reader_tests import SAMPLES_DIR, CATALOG_ID

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class DatabaseLoaderTests(TestCase):

    catalog_id = 'test_catalog'

    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()
        self.node = Node(catalog_id=self.catalog_id,
                         catalog_url=os.path.join(dir_path, 'full_ts_data.json'),
                         indexable=True)
        self.node.catalog = json.dumps(DataJson(self.node.catalog_url))
        self.node.save()

        self.init_datasets(self.node)
        self.loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)

    @staticmethod
    def init_datasets(node, whitelist=True):
        catalog_model, created = Catalog.objects.get_or_create(identifier=node.catalog_id)
        catalog = DataJson(json.loads(node.catalog))
        if created:
            catalog_model.title = catalog['title'],
            catalog_model.metadata = '{}'
            catalog_model.save()
        for dataset in catalog.get_datasets():
            dataset_model, created = Dataset.objects.get_or_create(
                catalog=catalog_model,
                identifier=dataset['identifier']
            )
            if created:
                dataset_model.metadata = '{}'
                dataset_model.indexable = whitelist
                dataset_model.save()

    def tearDown(self):
        Catalog.objects.filter(identifier=self.catalog_id).delete()

    def test_blacklisted_catalog_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))

        self.loader.run(catalog, self.catalog_id)
        meta = Catalog.objects.first().metadata
        meta = json.loads(meta)
        for field in settings.CATALOG_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_dataset_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))

        self.loader.run(catalog, self.catalog_id)
        meta = Dataset.objects.first().metadata
        meta = json.loads(meta)
        for field in settings.DATASET_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_distrib_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))

        self.loader.run(catalog, self.catalog_id)
        distribution = Distribution.objects.first()
        meta = distribution.metadata
        meta = json.loads(meta)
        for field in settings.DISTRIBUTION_BLACKLIST:
            self.assertTrue(field not in meta)

    def test_blacklisted_field_meta(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))

        self.loader.run(catalog, self.catalog_id)
        distribution = Distribution.objects.first()
        for field_model in distribution.field_set.all():
            for field in settings.FIELD_BLACKLIST:
                self.assertTrue(field not in field_model.metadata)

    def test_datasets_loaded_are_not_indexable(self):
        Catalog.objects.all().delete()  # Fuerza a recrear los modelos

        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.node.catalog = json.dumps(catalog)
        self.init_datasets(self.node, whitelist=False)
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=False)
        loader.run(catalog, self.catalog_id)
        dataset = Catalog.objects.get(identifier=CATALOG_ID).dataset_set

        self.assertEqual(dataset.count(), 1)
        self.assertFalse(dataset.first().indexable)

    def test_change_series_distribution(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))

        self.loader.run(catalog, self.catalog_id)
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data_changed_distribution.json'))
        models = [Catalog, Dataset, Distribution, Field]
        for model in models:
            model.objects.all().update(present=False, updated=False)
        loader = DatabaseLoader(self.task, read_local=True, default_whitelist=True)
        loader.run(catalog, self.catalog_id)

        # Al cambiar identificadores, se duplican los modelos, pero solo uno queda presente
        self.assertEqual(Field.objects.filter(identifier="212.1_PSCIOS_IOS_0_0_25").count(), 2)
        self.assertEqual(Field.objects.filter(identifier="212.1_PSCIOS_IOS_0_0_25",
                                              present=True, updated=True).count(), 1)

    def test_same_dataset_identifier_only_one_error(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        catalog1 = self.loader.run(catalog, self.catalog_id + "1")
        catalog2 = self.loader.run(catalog, self.catalog_id + "2")

        catalog.datasets[0]['distribution'] = 'garbage'
        self.loader.run(catalog, self.catalog_id + "1")

        self.assertTrue(Dataset.objects.get(catalog=catalog1,
                                            identifier='99db6631-d1c9-470b-a73e-c62daa32c777').error)
        self.assertFalse(Dataset.objects.get(catalog=catalog2,
                                             identifier='99db6631-d1c9-470b-a73e-c62daa32c777').error)

    def test_same_distribution_identifier_only_one_error(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        catalog1 = self.loader.run(catalog, self.catalog_id + "1")
        catalog2 = self.loader.run(catalog, self.catalog_id + "2")
        dataset1 = Dataset.objects.get(catalog=catalog1,
                                       identifier='99db6631-d1c9-470b-a73e-c62daa32c777')
        dataset2 = Dataset.objects.get(catalog=catalog2,
                                       identifier='99db6631-d1c9-470b-a73e-c62daa32c777')

        catalog.distributions[0].pop('downloadURL')
        self.loader.run(catalog, self.catalog_id + "1")

        self.assertTrue(Distribution.objects.get(dataset=dataset1, identifier='212.1').error)
        self.assertFalse(Distribution.objects.get(dataset=dataset2, identifier='212.1').error)

    def test_no_url_distribution_triggers_error_bit(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'distribution_missing_downloadurl.json'))
        self.loader.run(catalog, self.catalog_id)
        invalid_distribution = Distribution.objects.get(identifier='212.1')
        # Marca la distribucion como erronea
        self.assertTrue(invalid_distribution.error)
        # Pero igualmente crea los fields
        self.assertEqual(4, Field.objects.filter(distribution=invalid_distribution).count())

    def test_loader_downloads_resource_if_full_run(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.task.indexing_mode = ReadDataJsonTask.COMPLETE_RUN
        self.loader._read_file = MagicMock(return_value=True)
        self.loader.run(catalog, self.catalog_id)
        self.loader._read_file.assert_called()

    def test_loader_doesnt_download_resource_if_metadata_only_run(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.task.indexing_mode = ReadDataJsonTask.METADATA_ONLY
        self.loader._read_file = MagicMock(return_value=True)
        self.loader.run(catalog, self.catalog_id)
        self.loader._read_file.assert_not_called()
