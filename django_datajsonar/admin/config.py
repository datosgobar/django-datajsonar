
from django.contrib import admin

from django_datajsonar.admin.singleton_admin import SingletonAdmin
from django_datajsonar.models.config import IndexingConfig


@admin.register(IndexingConfig)
class IndexingConfigAdmin(SingletonAdmin):
    pass
