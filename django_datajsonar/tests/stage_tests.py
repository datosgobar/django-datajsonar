from django.test import TestCase
from mock import Mock

from django_datajsonar.models import Stage, Node

test_job = Mock()


class StageTests(TestCase):

    def setUp(self) -> None:
        test_job.reset_mock()

    def test_start_stage_calls_task(self):
        stage = Stage.objects.create(name='test_stage',
                                     queue='default',
                                     callable_str='django_datajsonar.tests.stage_tests.test_job')

        stage.open_stage()
        test_job.delay.assert_called_once()

    def test_start_stage_with_node_passes_the_node(self):
        stage = Stage.objects.create(name='test_stage',
                                     queue='default',
                                     callable_str='django_datajsonar.tests.stage_tests.test_job')

        node = Node.objects.create(catalog_id='test_catalog', catalog_url='http://testcatalog.com', indexable=True)
        stage.open_stage(node)
        test_job.delay.assert_called_once()
        test_job.delay.assert_called_with(node)
