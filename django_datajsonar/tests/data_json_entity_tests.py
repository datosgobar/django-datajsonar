import datetime

import dateutil.tz
import pytz
from freezegun import freeze_time

from django_datajsonar.models.data_json_entity_mixin import DataJsonEntityMixin
from django_datajsonar.strings import DEFAULT_TIME_ZONE

from django_datajsonar.tests.mixin_test_case import ModelMixinTestCase


class DataJsonEntityTests(ModelMixinTestCase):
    mixin = DataJsonEntityMixin

    def setUp(self):
        super(DataJsonEntityTests, self).setUp()
        self.entity = self.model()

    def test_update_metadata(self):
        self.entity.update_metadata({'test_field': 'test_value'})

        self.assertEqual(self.entity.get_metadata()['test_field'], 'test_value')

    def test_update_metadata_sets_model_as_updated(self):
        self.entity.update_metadata({'test_field': 'test_value'})

        self.assertTrue(self.entity.updated)

    def test_metadata_not_considered_new_if_already_saved(self):
        self.entity.save()
        self.entity.update_metadata({'test_field': 'test_value'})
        self.assertFalse(self.entity.new)

    def test_entity_considered_new_if_not_saved_before(self):
        self.entity.update_metadata({'test_field': 'test_value'})
        self.assertTrue(self.entity.new)

    def test_save_of_same_metadata_sets_entity_as_not_updated(self):
        self.entity.update_metadata({'test_field': 'test_value'})
        self.entity.update_metadata({'test_field': 'test_value'})
        self.assertFalse(self.entity.updated)

    def test_entity_always_considered_updated_on_data_change(self):
        self.entity.update_metadata({'test_field': 'test_value'})
        self.entity.update_metadata({'test_field': 'test_value'}, data_change=True)
        self.assertTrue(self.entity.updated)

    def test_entity_always_considered_updated_on_children_updated(self):
        self.entity.update_metadata({'test_field': 'test_value'})
        self.entity.update_metadata({'test_field': 'test_value'}, updated_children=True)
        self.assertTrue(self.entity.updated)

    @freeze_time("2019-01-01 00:00:00")
    def test_default_issued_is_current_timezone(self):
        self.entity.update_metadata({'test_field': 'test_value'})
        self.assertEqual(self.entity.issued,
                         datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=pytz.utc))

    def test_issued_is_read_from_metadata(self):
        self.entity.update_metadata({'test_field': 'test_value',
                                     'issued': '2016-04-14T19:48:05.433640'})

        self.assertEqual(self.entity.issued,
                         datetime.datetime(2016, 4, 14, 19, 48, 5, 433640,
                                           tzinfo=dateutil.tz.gettz(DEFAULT_TIME_ZONE)))

    def test_issued_date_read_correctly(self):
        self.entity.update_metadata({'test_field': 'test_value',
                                     'issued': '2016-04-14'})
        self.assertEqual(self.entity.issued,
                         datetime.datetime(2016, 4, 14, 0, 0, 0,
                                           tzinfo=dateutil.tz.gettz(DEFAULT_TIME_ZONE)))
