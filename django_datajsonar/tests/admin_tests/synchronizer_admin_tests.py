from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from mock import patch

from django_datajsonar.models import Synchronizer, Stage


@patch('django_datajsonar.admin.synchronizer.Synchronizer')
class SynchronizerAdminTests(TestCase):
    def setUp(self):
        new_stage = Stage.objects.create(callable_str='django_datajsonar.tests.synchro_tests.callable_method',
                                         task='django_datajsonar.models.ReadDataJsonTask',
                                         queue='indexing', next_stage=None, name='stage')
        self.synchro = Synchronizer.objects.create(start_stage=new_stage,
                                                   name='test_synchro')

        # admin auth
        self.client.force_login(User.objects.create(username='test_user', is_staff=True))

    def test_start_manually_if_already_started_fails(self, mock_synchro):
        self.synchro.status = Synchronizer.RUNNING
        self.synchro.save()

        self.client.post(reverse('admin:django_datajsonar_synchronizer_start_synchro',
                                 args=(self.synchro.id,)))

        mock_synchro.begin_stage.assert_not_called()
