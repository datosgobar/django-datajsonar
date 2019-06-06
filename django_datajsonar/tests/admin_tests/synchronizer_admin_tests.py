from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from mock import patch

from django_datajsonar.models import Synchronizer, Stage, Node


@patch('django_datajsonar.admin.synchronizer.Synchronizer.begin_stage')
class SynchronizerAdminTests(TestCase):
    def setUp(self):
        Node.objects.create(indexable=True, catalog_id='test_catalog', catalog_url='localhost:8000/data.json')
        new_stage = Stage.objects.create(callable_str='django_datajsonar.tests.synchro_tests.callable_method',
                                         task='django_datajsonar.models.ReadDataJsonTask',
                                         queue='indexing', next_stage=None, name='stage')
        self.synchro = Synchronizer.objects.create(start_stage=new_stage,
                                                   name='test_synchro')

        # admin auth
        self.client.force_login(User.objects.create(username='test_user', is_staff=True))

        self.url = reverse('admin:django_datajsonar_synchronizer_start_synchro',
                           args=(self.synchro.id,))

    def test_start_manually_if_already_started_fails(self, begin_stage):
        self.synchro.status = Synchronizer.RUNNING
        self.synchro.save()

        self.client.post(self.url)

        begin_stage.assert_not_called()

    def test_begin_stage_is_called(self, begin_stage):
        self.client.post(self.url, {'node': 1})
        begin_stage.assert_called_once()

    def test_run_manually_with_no_node(self, begin_stage):
        self.client.post(self.url)
        begin_stage.assert_called_once()
