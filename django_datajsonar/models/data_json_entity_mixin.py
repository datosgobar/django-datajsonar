import json

import dateutil.tz
from django.db import models
from django.utils import timezone
from iso8601 import iso8601
from django_datajsonar.strings import DEFAULT_TIME_ZONE


class DataJsonEntityMixin(models.Model):
    class Meta:
        abstract = True

    metadata = models.TextField()
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='', blank=True)

    issued = models.DateTimeField(null=True, blank=True)

    def update_metadata(self, new_metadata: dict, updated_children=False, data_change=False):
        previous_meta = self.get_metadata()
        updated = (new_metadata != previous_meta or data_change or updated_children)
        self.updated = updated
        self.metadata = json.dumps(new_metadata)
        self.new = self.pk is None
        self.present = True

        if new_metadata.get('issued'):
            self.issued = iso8601.parse_date(new_metadata.get('issued'),
                                             default_timezone=dateutil.tz.gettz(DEFAULT_TIME_ZONE))
        else:
            self.issued = timezone.now()

    def get_metadata(self):
        return json.loads(self.metadata or '{}')
