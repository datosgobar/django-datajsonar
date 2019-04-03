from django.test import TestCase
from mock import Mock, patch

from django_datajsonar.models import Synchronizer, Stage


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
