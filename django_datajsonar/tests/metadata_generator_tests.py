#! coding: utf-8
import os

from datetime import datetime

from django.test import TestCase

from django_datajsonar.models.node import Jurisdiction, NodeMetadata, Node
from django_datajsonar.models.metadata import ProjectMetadata, Publisher, \
    Language, Spatial

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class NodeRegisterFileTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up project metadata
        project_metadata = ProjectMetadata.get_solo()
        project_metadata.title = 'Test project'
        project_metadata.description = 'Test description'
        project_metadata.homepage = 'http://test.homepage'
        project_metadata.issued = datetime.today()
        project_metadata.save()

        publisher = Publisher.get_solo()
        publisher.name = 'pub_name'
        publisher.mbox = 'pub_mbox'
        publisher.save()

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
            node = Node.objects.create(catalog_id='catalog_id' + i_str,
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
                url_datosgobar='http://test.url',
                url_homepage='http://test.url',
                url_json='http://test.url',
                url_xlsx='http://test.url',
                node=nodes[i])
            nodes_meta.append(node_meta)

    def test_project_metadata_values(self):
        pass

    def test_jurisdiction_values(self):
        pass

    def test_modified_field_is_updated_correctly(self):
        pass

    def test_missing_values_appear_as_none(self):
        pass
