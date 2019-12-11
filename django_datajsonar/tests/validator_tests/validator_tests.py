import json

import requests_mock
from django.test import TestCase, Client
from django.urls import reverse

from django_datajsonar.tests.helpers import open_catalog
from django_datajsonar.views import ValidatorView


class ValidatorTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.validator_url = reverse('django_datajsonar:validator')
        cls.validator_success_url = reverse('django_datajsonar:validator_success')

    @requests_mock.mock()
    def test_valid_catalog_redirects_to_success_page(self, mock):
        with open_catalog('sample_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'json'
            }

            response = self.client.post(self.validator_url, form_data)

            self.assertEqual(response.url, self.validator_success_url)

    @requests_mock.mock()
    def test_invalid_catalog_redirects_to_success_page_with_validation_messages(self, mock):
        with open_catalog('invalid_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'json'
            }

            response = self.client.post(self.validator_url, form_data, follow=True)
            self.assertEqual(response.context['request'].get_full_path(),
                             self.validator_success_url)

            message = list(response.context['messages'])[0].message
            expected_validation_message = "En dataset Forestales - Tamaño y cantidad de focos" \
                                          " de incendios: 'cantidad-de-focos-por-tamaño-y-por" \
                                          "-año .csv' is not valid under any of the given schemas"
            self.assertIn(expected_validation_message, message)

    def test_invalid_url_redirects_to_form(self):
        form_data = {
            'catalog_url': 'this_is_not_a_url',
            'format': 'json'
        }

        response = self.client.post(self.validator_url, form_data)
        self.assertIn('validator.html', response.template_name)

        message = str(list(response.context['messages'])[0])
        self.assertIn("Error descargando el catálogo", message)

    @requests_mock.mock()
    def test_redirects_to_form_if_formats_differ(self, mock):
        with open_catalog('invalid_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'xlsx'
            }

            response = self.client.post(self.validator_url, form_data)
            self.assertIn('validator.html', response.template_name)

            message = str(list(response.context['messages'])[0])
            self.assertIn("El formato ingresado y el del catálogo deben coincidir", message)
