import json

from django.db import models
from django.utils import timezone


class DataJsonEntityMixin(models.Model):
    class Meta:
        abstract = True

    metadata = models.TextField()
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='')

    def update_metadata(self, new_metadata, updated_children=False, data_change=False):
        previous_meta = self.get_metadata()
        updated = (new_metadata != previous_meta or data_change or updated_children)
        self.updated = updated
        self.metadata = json.dumps(new_metadata)
        self.new = self.pk is None
        self.present = True

    def get_metadata(self):
        return json.loads(self.metadata or '{}')
