#! coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType

from solo.admin import SingletonModelAdmin

from django_datajsonar.admin.singleton_admin import SingletonAdmin
from django_datajsonar.models import Metadata, ProjectMetadata,\
    Language, Publisher, Spatial


class EnhancedMetaFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('catalog', 'Catálogo'),
            ('dataset', 'Dataset'),
            ('distribution', 'Distribución'),
            ('field', 'Campo'),
        )

    title = 'Instancia'
    parameter_name = 'content_object'

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(content_type=ContentType.objects.get(app_label='django_datajsonar',
                                                                    model=self.value()))


@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_filter = (EnhancedMetaFilter, 'key')
    list_display = ('get_entity_content_type', 'get_entity_identifier', 'get_entity_title', 'key', 'value')

    def get_entity_content_type(self, metadata):
        result = str(metadata.content_type).capitalize()
        return result
    get_entity_content_type.short_description = 'Tipo Entidad'

    def get_entity_title(self, metadata):
        result = metadata.content_object.title
        return result
    get_entity_title.short_description = 'Título'

    def get_entity_identifier(self, metadata):
        result = metadata.content_object.identifier or ''
        return result
    get_entity_identifier.short_description = 'ID'


class LanguageAdmin(admin.TabularInline):
    model = Language


class PublisherAdmin(admin.TabularInline):
    model = Publisher


class SpatialAdmin(admin.TabularInline):
    model = Spatial


@admin.register(ProjectMetadata)
class ProjectMetadataAdmin(SingletonAdmin):
    inlines = [
        LanguageAdmin,
        PublisherAdmin,
        SpatialAdmin,
    ]
