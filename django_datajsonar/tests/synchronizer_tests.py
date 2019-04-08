from django.test import TestCase
from mock import Mock, patch

from django_datajsonar.models import Synchronizer, Stage, Node


@patch('django_datajsonar.models.synchronizer.Synchronizer.save')
class SynchronizerTests(TestCase):

    def test_start_synchronizer_begins_the_first_stage(self, *_):
        stage = Stage()
        stage.open_stage = Mock()
        Synchronizer(start_stage=stage).begin_stage()
        stage.open_stage.assert_called_once()

    def test_start_running_synchro_raises_exception(self, *_):
        with self.assertRaises(Exception):
            stage = Stage()
            stage.open_stage = Mock()
            Synchronizer(status=Synchronizer.RUNNING, start_stage=stage).begin_stage()

    def test_start_stage_for_node(self, *_):
        stage = Stage()
        stage.open_stage = Mock()
        node = Node.objects.create(catalog_id='test_catalog', catalog_url='http://catalog_url.com', indexable=True)
        Synchronizer(start_stage=stage).begin_stage(node=node)
        stage.open_stage.assert_called_with(node)
