#! coding: utf-8
import os

from django.test import TestCase

from django_datajsonar.indexing.catalog_reader import index_catalog
from django_datajsonar.models import ReadDataJsonTask, Node, Distribution
from django_datajsonar.utils.metadata_generator import \
    get_distributions_metadata

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class DistributionMetadataGenerator(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'sample_data.json')
    catalog_id = 'catalog_id'

    @classmethod
    def setUpTestData(cls):
        cls.task = ReadDataJsonTask.objects.create()
        cls.node = Node(catalog_id=cls.catalog_id, catalog_url=cls.catalog,
                        indexable=True)
        cls.node.save()
        index_catalog(cls.node, cls.task, read_local=True, whitelist=True)

    def test_catalog_model_values(self):
        result = get_distributions_metadata()
        for distribution in result:
            self.assertEqual('Datos Programación Macroeconómica',
                             distribution['dataset__catalog__title'])
            self.assertEqual('catalog_id',
                             distribution['dataset__catalog__identifier'])

    def test_dataset_model_values(self):
        result = get_distributions_metadata()
        for distribution in result:
            self.assertEqual('Oferta y Demanda Globales. '
                             'Datos desestacionalizados. Base 1993',
                             distribution['dataset__title'])
            self.assertEqual('1',
                             distribution['dataset__identifier'])

    def test_distribution_model_values(self):
        result = get_distributions_metadata()
        distribution = result[0]
        self.assertEqual('Oferta y Demanda Global. Precios constantes '
                         'desestacionalizados. Base 1993. Valores anuales.',
                         distribution['title'])
        self.assertEqual('1.1',
                         distribution['identifier'])
        self.assertEqual(
            'http://infra.datos.gob.ar/catalog/sspm/dataset/1/distribution/1.1/'
            'download/oferta-demanda-global-precios-constantes-'
            'desestacionalizados-base-1993-valores-anuales.csv',
            distribution['download_url']
        )

    def test_missing_values_are_passed_as_none(self):
        distribution_model = Distribution.objects.get(identifier='1.1')
        distribution_model.download_url = None
        distribution_model.save()
        result = get_distributions_metadata()
        distribution = result[0]
        self.assertIsNone(distribution['download_url'])
