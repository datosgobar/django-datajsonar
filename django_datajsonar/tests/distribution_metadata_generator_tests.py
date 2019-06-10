#! coding: utf-8
import os

from django.conf import settings
from django.test import TestCase

from django_datajsonar.indexing.catalog_reader import index_catalog
from django_datajsonar.models import ReadDataJsonTask, Node, Distribution
from django_datajsonar.tests.helpers import create_node
from django_datajsonar.utils.metadata_generator import \
    get_distributions_metadata

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class DistributionMetadataGenerator(TestCase):
    catalog = os.path.join(SAMPLES_DIR, 'sample_data.json')
    catalog_id = 'catalog_id'
    catalog_two = os.path.join(SAMPLES_DIR, 'another_catalog.json')
    catalog_two_id = 'enargas'

    @classmethod
    def setUpTestData(cls):
        cls.task = ReadDataJsonTask.objects.create(
            indexing_mode=ReadDataJsonTask.METADATA_ONLY)
        cls.node = Node(catalog_id=cls.catalog_id, catalog_url=cls.catalog,
                        indexable=True)
        cls.node.save()
        index_catalog(cls.node, cls.task, read_local=True, whitelist=True)

        cls.node_two = create_node(cls.catalog_two, cls.catalog_two_id)
        index_catalog(cls.node_two, cls.task, read_local=True, whitelist=True)

    def test_catalog_model_values(self):
        result = get_distributions_metadata()
        for distribution in result[:2]:
            self.assertEqual('Datos Programación Macroeconómica',
                             distribution['dataset__catalog__title'])
            self.assertEqual('catalog_id',
                             distribution['dataset__catalog__identifier'])
        for distribution in result[2:]:
            self.assertEqual('Datos abiertos del Ente Nacional Regulador del Gas',
                             distribution['dataset__catalog__title'])
            self.assertEqual('enargas',
                             distribution['dataset__catalog__identifier'])

    def test_dataset_model_values(self):
        result = get_distributions_metadata()
        for distribution in result[:2]:
            self.assertEqual('Oferta y Demanda Globales. '
                             'Datos desestacionalizados. Base 1993',
                             distribution['dataset__title'])
            self.assertEqual('1',
                             distribution['dataset__identifier'])
        for distribution in result[2:12]:
            self.assertEqual('Información geográfica del ENARGAS',
                             distribution['dataset__title'])
            self.assertEqual('1',
                             distribution['dataset__identifier'])
        for distribution in result[12:]:
            self.assertEqual('Plan de inversiones de las Licenciatarias de '
                             'Transporte y Distribución de Gas',
                             distribution['dataset__title'])
            self.assertEqual('2',
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

    def test_distribution_metadata_field_values(self):
        result = get_distributions_metadata()
        distribution = result[0]
        self.assertEqual('https://www.minhacienda.gob.ar/secretarias/'
                         'politica-economica/programacion-macroeconomica/',
                         distribution['accessURL'])
        self.assertEqual('file', distribution['type'])
        self.assertEqual('CSV', distribution['format'])
        self.assertNotIn('metadata', distribution)

    def test_dataset_metadata_field_values(self):
        result = get_distributions_metadata()
        distribution = result[0]
        self.assertEqual('Componentes desestacionalizados de la oferta y '
                         'demanda globales a precios de 1993.',
                         distribution['dataset_description'])
        self.assertEqual('Subsecretaría de Programación Macroeconómica.',
                         distribution['dataset_publisher'])
        self.assertEqual('datoseconomicos@mecon.gov.ar',
                         distribution['dataset_publisher_mail'])
        self.assertEqual('datoseconomicos@mecon.gov.ar',
                         distribution['dataset_publisher_mail'])
        self.assertEqual('Instituto Nacional de Estadística y Censos (INDEC)',
                         distribution['dataset_source'])
        self.assertEqual('actividad', distribution['dataset_theme'])
        self.assertEqual('ECON', distribution['dataset_superTheme'])

    def test_catalog_metadata_field_values(self):
        result = get_distributions_metadata()
        distribution = result[0]
        self.assertEqual('Subsecretaría de Programación Macroeconómica.',
                         distribution['catalog_publisher'])

    def test_missing_metadata_values_passed_as_none(self):
        result = get_distributions_metadata()
        distribution = result[1]
        self.assertIsNone(distribution['type'])
        self.assertIsNone(distribution['dataset_license'])

    def test_rows_ordered_by_catalog_identifier(self):
        result = get_distributions_metadata()
        first = result[1]
        second = result[2]
        self.assertTrue(
            first['dataset__catalog__identifier'] < second['dataset__catalog__identifier'])

    def test_rows_ordered_by_dataset_identifier(self):
        result = get_distributions_metadata()
        first = result[11]
        second = result[12]
        self.assertTrue(first['dataset__identifier'] < second['dataset__identifier'])

    def test_rows_ordered_by_distribution_identifier(self):
        result = get_distributions_metadata()
        first_distribution = result[5]
        second_distribution = result[6]
        self.assertTrue(first_distribution['identifier'] <= second_distribution['identifier'])
