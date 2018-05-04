#! coding: utf-8


from django.test import TestCase
from django_datajsonar.models import Catalog, Metadata


class EnhancedMetaTests(TestCase):

    def test_add_meta_to_catalog(self):

        catalog = Catalog()
        catalog.save()  # Necesario save previo para usar generic foreign keys

        test_key, test_value = 'Test key', 'test value'
        catalog.enhanced_meta.create(key=test_key, value=test_value)

        self.assertEqual(Metadata.objects.count(), 1)
        self.assertEqual(Metadata.objects.first().key, test_key)
        self.assertEqual(Metadata.objects.first().value, test_value)
