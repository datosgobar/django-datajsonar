from django.contrib import admin

from django_datajsonar.models import Jurisdiction, Stage
from . import synchronizer, data_json, metadata, node, repeatable_job, tasks

admin.site.register(Jurisdiction)
admin.site.register(Stage)
