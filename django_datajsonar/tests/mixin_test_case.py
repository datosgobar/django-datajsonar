from django.db import connection
from django.core.management.color import no_style
from django.db.models.base import ModelBase
from django.test import TestCase


class ModelMixinTestCase(TestCase):
    """
    Base class for tests of model mixins. To use, subclass and specify
    the mixin class variable. A model using the mixin will be made
    available in self.model.
    """

    @classmethod
    def setUpClass(cls):
        super(ModelMixinTestCase, cls).setUpClass()
        # Create a dummy model which extends the mixin
        cls.model = ModelBase('__TestModel__' + cls.mixin.__name__, (cls.mixin,),
                              {'__module__': cls.mixin.__module__})

        # Create the schema for our test model
        cls._style = no_style()

        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        cls._cursor = connection.cursor()

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)
