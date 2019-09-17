#! coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from django_datajsonar.actions import process_node_register_file_action
from django_datajsonar.models import NodeMetadata, DatasetIndexingFile, NodeRegisterFile, Node

from django_datajsonar.tasks import bulk_whitelist


class BaseRegisterFileAdmin(admin.ModelAdmin):
    actions = ['process_register_file']
    list_display = ('__unicode__', 'state', )
    readonly_fields = ('created', 'modified', 'state', 'logs')

    def process_register_file(self, _, queryset):
        raise NotImplementedError
    process_register_file.short_description = 'Ejecutar'

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseRegisterFileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['uploader'].initial = request.user
        return form


@admin.register(NodeRegisterFile)
class NodeRegisterFileAdmin(BaseRegisterFileAdmin):

    def process_register_file(self, _, queryset):
        for model in queryset:
            model.state = NodeRegisterFile.state = NodeRegisterFile.PROCESSING
            model.logs = u'-'
            model.save()
            process_node_register_file_action(model)


@admin.register(DatasetIndexingFile)
class DatasetIndexingFileAdmin(BaseRegisterFileAdmin):
    def process_register_file(self, _, queryset):
        for model in queryset:
            model.state = DatasetIndexingFile.state = DatasetIndexingFile.PROCESSING
            model.logs = u'-'  # Valor default mientras se ejecuta
            model.save()
            bulk_whitelist.delay(model.id)


class InlineNodeMetadata(admin.StackedInline):
    model = NodeMetadata


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('catalog_id', 'indexable', 'timezone')
    exclude = ('catalog',)
    inlines = (InlineNodeMetadata,)
    actions = ('make_indexable', 'make_unindexable')

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no federable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como federable'
