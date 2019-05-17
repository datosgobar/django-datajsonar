#! coding: utf-8
from __future__ import unicode_literals

import os
from collections import OrderedDict
from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils.timezone import now
from freezegun import freeze_time

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from django_datajsonar.models.metadata import ProjectMetadata, Publisher, \
    Language, Spatial
from django_datajsonar.models.node import Jurisdiction, NodeMetadata, Node
from django_datajsonar.utils.metadata_generator import get_project_metadata, \
    get_jurisdiction_list_metadata, last_modified_date
from django_datajsonar.utils.metadata_csv_writer import \
    flatten_jurisdiction_list_metadata, translate_fields
dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class MetadataGeneratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up project metadata
        project_metadata = ProjectMetadata.get_solo()
        project_metadata.title = 'Test project'
        project_metadata.description = 'Test description'
        project_metadata.homepage = 'http://test.homepage'
        project_metadata.issued = date(2000, 1, 1)
        project_metadata.version = 'v.test'
        project_metadata.save()

        Publisher.objects.create(name='pub_name',
                                 mbox='pub_mbox',
                                 project_metadata=project_metadata)
        Language.objects.create(language='spa',
                                project_metadata=project_metadata)
        Language.objects.create(language='swa',
                                project_metadata=project_metadata)
        Spatial.objects.create(spatial='ARG',
                               project_metadata=project_metadata)

        # jurisdictions
        jurs = []
        for i in range(0, 2):
            i_str = str(i)
            jur = Jurisdiction.objects.create(
                jurisdiction_title='jurisdiction_' + i_str,
                jurisdiction_id='id_' + i_str,
                argentinagobar_id='gobar_' + i_str)
            jurs.append(jur)

        # nodes
        nodes = []
        for i in range(0, 3):
            i_str = str(i)
            node = Node.objects.create(catalog_id='catalog_id_' + i_str,
                                       catalog_url='http://test.url',
                                       indexable=True)
            nodes.append(node)

        # node metadata
        nodes_meta = []
        for i in range(0, 3):
            i_str = str(i)
            node_meta = NodeMetadata.objects.create(
                label='metadata_' + i_str,
                category='no-central',
                type='andino',
                jurisdiction=jurs[i // 2],
                url_datosgobar='http://test.url.datos.' + i_str,
                url_homepage='http://test.url.home.' + i_str,
                url_json='http://test.url.json.' + i_str,
                url_xlsx='http://test.url.xlsx.' + i_str,
                node=nodes[i])
            nodes_meta.append(node_meta)

    def test_project_metadata_values(self):
        expected = {
            'title': 'Test project',
            'description': 'Test description',
            'homepage': 'http://test.homepage',
            'version': 'v.test',
            'language': ['spa', 'swa'],
            'spatial': ['ARG'],
            'publisher': {'name': 'pub_name', 'mbox': 'pub_mbox'},
            'issued': date(2000, 1, 1),
            'modified': datetime.today().date(),
            'jurisdiction_count': 2,
            'catalog_count': 3
        }
        result = get_project_metadata()
        self.assertDictEqual.__self__.maxDiff = None
        self.assertDictEqual(expected, result)

    def test_jurisdiction_values(self):
        expected = [
            {'title': 'jurisdiction_0',
             'argentinagobar_id': 'gobar_0',
             'catalogs': [
                 {'id': 'catalog_id_0',
                  'label': 'metadata_0',
                  'category': 'no-central',
                  'type': 'andino',
                  'published': True,
                  'url_datosgobar': 'http://test.url.datos.0',
                  'url_homepage': 'http://test.url.home.0',
                  'url_json': 'http://test.url.json.0',
                  'url_xlsx': 'http://test.url.xlsx.0',
                  },
                 {'id': 'catalog_id_1',
                  'label': 'metadata_1',
                  'category': 'no-central',
                  'type': 'andino',
                  'published': True,
                  'url_datosgobar': 'http://test.url.datos.1',
                  'url_homepage': 'http://test.url.home.1',
                  'url_json': 'http://test.url.json.1',
                  'url_xlsx': 'http://test.url.xlsx.1',
                  },
             ]},
            {'title': 'jurisdiction_1',
             'argentinagobar_id': 'gobar_1',
             'catalogs': [
                 {'id': 'catalog_id_2',
                  'label': 'metadata_2',
                  'category': 'no-central',
                  'type': 'andino',
                  'published': True,
                  'url_datosgobar': 'http://test.url.datos.2',
                  'url_homepage': 'http://test.url.home.2',
                  'url_json': 'http://test.url.json.2',
                  'url_xlsx': 'http://test.url.xlsx.2',
                  }
             ]}
        ]
        result = get_jurisdiction_list_metadata()
        self.assertListEqual.__self__.maxDiff = None
        self.assertListEqual(expected, result)

    def test_modified_field_is_updated_correctly(self):
        with freeze_time(lambda: now() + timedelta(days=15)):
            node_meta = NodeMetadata.objects.get(label='metadata_0')
            node_meta.type = 'ckan'
            node_meta.save()
            node_meta.refresh_from_db()
        self.assertEqual((now() + timedelta(days=15)).date(),
                         last_modified_date())

    def test_project_metadata_is_updated_correctly(self):
        project_meta = ProjectMetadata.get_solo()
        project_meta.title = 'new title'
        project_meta.description = None
        project_meta.save()
        result = get_project_metadata()
        self.assertTrue('title' in result)
        self.assertEqual('new title', result['title'])
        self.assertTrue('description' in result)
        self.assertIsNone(result['description'])

    def test_jurisdiction_metadata_is_updated_correctly(self):
        jurisdiction_meta = Jurisdiction.objects.get(jurisdiction_id='id_1')
        jurisdiction_meta.jurisdiction_title = 'new title'
        jurisdiction_meta.argentinagobar_id = None
        jurisdiction_meta.save()
        result = get_jurisdiction_list_metadata()[1]
        self.assertTrue('title' in result)
        self.assertEqual('new title', result['title'])
        self.assertTrue('argentinagobar_id' in result)
        self.assertIsNone(result['argentinagobar_id'])

    def test_node_metadata_is_updated_correctly(self):
        node_meta = NodeMetadata.objects.get(label='metadata_1')
        node_meta.category = 'central'
        node_meta.type = None
        node_meta.save()
        result = get_jurisdiction_list_metadata()[0]['catalogs'][1]
        self.assertTrue('category' in result)
        self.assertEqual('central', result['category'])
        self.assertTrue('type' in result)
        self.assertIsNone(result['type'])

    def test_unnaffiliated_jurisdiction(self):
        Jurisdiction.objects.create(jurisdiction_id='id_3',
                                    jurisdiction_title='unaffiliated_title',
                                    argentinagobar_id='00000')
        result = get_jurisdiction_list_metadata()
        self.assertEqual(3, len(result))
        self.assertEqual(0, len(result[2]['catalogs']))

    def test_unnaffiliated_metadata(self):
        unaffiliated_node = Node.objects.create(catalog_id='unaffiliated_id',
                                                indexable=True)
        NodeMetadata.objects.create(node=unaffiliated_node)
        project = get_project_metadata()
        jurisdictions = get_jurisdiction_list_metadata()
        self.assertEqual(3, project['catalog_count'])
        self.assertEqual(2, len(jurisdictions[0]['catalogs']))
        self.assertEqual(1, len(jurisdictions[1]['catalogs']))

    def test_jurisdiction_metadata_flatten(self):
        expected = [
            {'id': 'catalog_id_0',
             'label': 'metadata_0',
             'category': 'no-central',
             'type': 'andino',
             'published': True,
             'url_datosgobar': 'http://test.url.datos.0',
             'url_homepage': 'http://test.url.home.0',
             'url_json': 'http://test.url.json.0',
             'url_xlsx': 'http://test.url.xlsx.0',
             'title': 'jurisdiction_0',
             'argentinagobar_id': 'gobar_0',
             },
            {'id': 'catalog_id_1',
             'label': 'metadata_1',
             'category': 'no-central',
             'type': 'andino',
             'published': True,
             'url_datosgobar': 'http://test.url.datos.1',
             'url_homepage': 'http://test.url.home.1',
             'url_json': 'http://test.url.json.1',
             'url_xlsx': 'http://test.url.xlsx.1',
             'title': 'jurisdiction_0',
             'argentinagobar_id': 'gobar_0',
             },
            {'id': 'catalog_id_2',
             'label': 'metadata_2',
             'category': 'no-central',
             'type': 'andino',
             'published': True,
             'url_datosgobar': 'http://test.url.datos.2',
             'url_homepage': 'http://test.url.home.2',
             'url_json': 'http://test.url.json.2',
             'url_xlsx': 'http://test.url.xlsx.2',
             'title': 'jurisdiction_1',
             'argentinagobar_id': 'gobar_1',
             }
        ]

        result = flatten_jurisdiction_list_metadata(
            get_jurisdiction_list_metadata())
        self.assertDictEqual.__self__.maxDiff = None
        self.assertListEqual(expected, result)

    def test_metadata_translation(self):
        test_trasnslation = OrderedDict({
            "id": "translation_1",
            "label": "translation_2",
            "url_json": "translation_3",
            "url_xlsx": "translation_4",
            "url_datosgobar": "translation_5",
            "url_homepage": "translation_6",
        })
        expected = {
            "translation_1": 'catalog_id_0',
            "translation_2": 'metadata_0',
            "translation_3": 'http://test.url.json.0',
            "translation_4": 'http://test.url.xlsx.0',
            "translation_5": 'http://test.url.datos.0',
            "translation_6": 'http://test.url.home.0',
        }
        result = translate_fields(
            get_jurisdiction_list_metadata()[0]['catalogs'],
            test_trasnslation)
        result = result[0]
        self.assertDictEqual(expected, result)
