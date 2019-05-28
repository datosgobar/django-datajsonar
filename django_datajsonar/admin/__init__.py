from django.contrib import admin

from django_datajsonar.models import Jurisdiction
from django_datajsonar.models import Stage
from . import synchronizer, data_json, metadata, node, repeatable_job, tasks, config

admin.site.register(Jurisdiction)
admin.site.register(Stage)
