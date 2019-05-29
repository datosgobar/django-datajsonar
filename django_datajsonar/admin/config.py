
from django.contrib import admin

from solo.admin import SingletonModelAdmin

from django_datajsonar.models.config import IndexingConfig


@admin.register(IndexingConfig)
class IndexingConfigAdmin(SingletonModelAdmin):
    pass
