import os
from datetime import datetime

from django.db.models import Min
from django.test import TestCase
from freezegun import freeze_time
from iso8601 import iso8601
from pydatajson import DataJson

from django_datajsonar.indexing.database_loader import DatabaseLoader
from django_datajsonar.indexing.tests.reader_tests import SAMPLES_DIR
from django_datajsonar.models import Catalog, Dataset, Distribution, ReadDataJsonTask


class InferredMetadataTests(TestCase):

    catalog_id = 'test_catalog'

    def setUp(self):
        self.task = ReadDataJsonTask()
        self.task.save()

        self.loader = DatabaseLoader(self.task, read_local=True, default_whitelist=False)

    def test_catalog_issued_infers_as_oldest_dataset(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'two_datasets.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Catalog.objects.first().issued
        dataset_issued = Dataset.objects.aggregate(Min('issued'))['issued__min']
        self.assertEqual(issued.date(),
                         dataset_issued.date())

    def test_dataset_issued_infers_as_oldest_distribution(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'two_datasets.json'))
        self.loader.run(catalog, self.catalog_id)
        dataset = Dataset.objects.first()
        distribution_issued = Distribution.objects.filter(dataset=dataset). \
            aggregate(Min('issued'))['issued__min']
        self.assertEqual(dataset.issued.date(),
                         distribution_issued.date())

    @freeze_time("2019-01-01")
    def test_issued_dataset_metadata_inferred(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        del catalog["dataset"][0]['issued']
        self.loader.run(catalog, self.catalog_id)
        issued = Dataset.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime.now().date())

    @freeze_time("2019-01-01")
    def test_issued_distributed_metadata_inferred(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Distribution.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime.now().date())

    def test_catalog_issued_no_inference(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Catalog.objects.first().issued
        self.assertEqual(issued.date(),
                         iso8601.parse_date(catalog['issued']).date())

    def test_dataset_issued_no_inference(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Dataset.objects.first().issued
        self.assertEqual(issued.date(),
                         iso8601.parse_date(catalog.get_datasets()[0]['issued']).date())

    def test_distribution_issued_no_inference(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'full_ts_data.json'))
        catalog.get_datasets()[0]['distribution'][0]['issued'] = '2016-04-14'
        self.loader.run(catalog, self.catalog_id)
        issued = Distribution.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime(2016, 4, 14).date())

    @freeze_time("2019-01-01")
    def test_catalog_without_issued_dates(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'no_issued_dates.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Catalog.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime.now().date())

    @freeze_time("2019-01-01")
    def test_dataset_without_issued_dates(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'no_issued_dates.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Dataset.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime.now().date())

    @freeze_time("2019-01-01")
    def test_distribution_without_issued_dates(self):
        catalog = DataJson(os.path.join(SAMPLES_DIR, 'no_issued_dates.json'))
        self.loader.run(catalog, self.catalog_id)
        issued = Distribution.objects.first().issued
        self.assertEqual(issued.date(),
                         datetime.now().date())
