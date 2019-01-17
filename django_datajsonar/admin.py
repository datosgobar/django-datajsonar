#!coding=utf8
from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelformset_factory
from django.contrib import admin, messages
from django.contrib.admin import helpers, SimpleListFilter
from django.utils import timezone
from django.conf.urls import url
from django.contrib.contenttypes.admin import GenericTabularInline
from django.shortcuts import render, redirect

from scheduler.models import RepeatableJob
from scheduler.admin import RepeatableJobAdmin

from .views import config_csv
from .actions import process_node_register_file_action, confirm_delete
from .utils import download_config_csv, generate_stages
from .tasks import bulk_whitelist, read_datajson
from .models import DatasetIndexingFile, NodeRegisterFile, Node, NodeMetadata, ReadDataJsonTask, Metadata, Synchronizer, Stage
from .models import Catalog, Dataset, Distribution, Field, Jurisdiction
from .forms import ScheduleJobForm, SynchroForm, StageFormset, StageForm


class EnhancedMetaAdmin(GenericTabularInline):
    class Media:
        css = {
            'all': ('django_datajsonar/css/hide_title.css', )
        }

    model = Metadata
    extra = 0
    can_delete = False

    class Form(forms.ModelForm):
        class Meta:
            model = Metadata
            fields = ['key', 'value']

        key = forms.CharField()
        value = forms.CharField()

    form = Form

    def has_add_permission(self, request):
        # Borra el botoncito de add new
        return False


class CatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier', 'present', 'updated')
    search_fields = ('identifier', 'present', 'updated')
    readonly_fields = ('identifier',)
    list_filter = ('present', 'updated')

    inlines = (
        EnhancedMetaAdmin,
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, distinct = \
            super(CatalogAdmin, self).get_search_results(request, queryset, search_term)
        if not search_term:
            return queryset, distinct

        ids_to_remove = []
        for obj in queryset:
            if search_term not in (obj.identifier,):
                ids_to_remove.append(obj.id)

        return queryset.exclude(id__in=ids_to_remove), distinct


class DatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'identifier', 'catalog', 'present', 'updated', 'indexable', 'reviewed', 'last_reviewed')
    search_fields = ('identifier', 'catalog__identifier', 'present', 'updated', 'indexable')
    readonly_fields = ('identifier', 'catalog', 'reviewed', 'last_reviewed')
    actions = ['make_indexable', 'make_unindexable', 'generate_config_file',
               'mark_as_reviewed', 'mark_on_revision', 'mark_as_not_reviewed']

    list_filter = ('catalog__identifier', 'present', 'indexable', 'reviewed')

    def mark_as_reviewed(self, _, queryset):
        queryset.update(reviewed=Dataset.REVIEWED, last_reviewed=timezone.localdate())
    mark_as_reviewed.short_description = 'Marcar como revisado'

    def mark_on_revision(self, _, queryset):
        queryset.update(reviewed=Dataset.ON_REVISION, last_reviewed=timezone.localdate())
    mark_on_revision.short_description = 'Marcar en revisión'

    def mark_as_not_reviewed(self, _, queryset):
        queryset.update(reviewed=Dataset.NOT_REVIEWED, last_reviewed=timezone.localdate())
    mark_as_not_reviewed.short_description = 'Marcar como no revisado'

    inlines = (
        EnhancedMetaAdmin,
    )

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no indexable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como indexable'

    def generate_config_file(self, _, queryset):
        indexables = queryset.filter(indexable=True)
        return download_config_csv(indexables)
    generate_config_file.short_description = 'Generar csv de configuración'

    def get_urls(self):
        urls = super(DatasetAdmin, self).get_urls()
        extra_urls = [url(r'^federacion-config\.csv/$', config_csv, name='config_csv'), ]
        return extra_urls + urls

    def get_search_results(self, request, queryset, search_term):
        queryset, distinct = \
            super(DatasetAdmin, self).get_search_results(request, queryset, search_term)
        if not search_term:
            return queryset, distinct

        ids_to_remove = []
        for obj in queryset:
            if search_term not in (obj.identifier,):
                ids_to_remove.append(obj.id)

        return queryset.exclude(id__in=ids_to_remove), distinct


class DistributionAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'get_dataset_title', 'get_catalog_id', 'last_updated', 'present', 'updated')
    search_fields = ('identifier', 'dataset__identifier', 'dataset__catalog__identifier')
    list_filter = ('dataset__catalog__identifier', )

    inlines = (
        EnhancedMetaAdmin,
    )

    def get_dataset_title(self, obj):
        return obj.dataset.title
    get_dataset_title.short_description = 'Dataset'
    get_dataset_title.admin_order_field = 'dataset__title'

    def get_catalog_id(self, obj):
        return obj.dataset.catalog.identifier
    get_catalog_id.short_description = 'Catalog'
    get_catalog_id.admin_order_field = 'dataset__catalog__identifier'

    def get_search_results(self, request, queryset, search_term):
        queryset, distinct = \
            super(DistributionAdmin, self).get_search_results(request, queryset, search_term)
        if not search_term:
            return queryset, distinct

        ids_to_remove = []
        for obj in queryset:
            if search_term not in (obj.identifier, obj.dataset.identifier):
                ids_to_remove.append(obj.id)

        return queryset.exclude(id__in=ids_to_remove), distinct


class FieldAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'identifier', 'get_distribution_title', 'get_dataset_title', 'get_catalog_id')
    search_fields = (
        'distribution__identifier',
        'distribution__dataset__identifier',
        'distribution__dataset__catalog__identifier'
    )
    list_filter = (
        'distribution__dataset__catalog__identifier',
    )

    inlines = (
        EnhancedMetaAdmin,
    )

    def get_catalog_id(self, obj):
        return obj.distribution.dataset.catalog.identifier
    get_catalog_id.short_description = 'Catalog'
    get_catalog_id.admin_order_field = 'distribution__dataset__catalog__identifier'

    def get_dataset_title(self, field):
        return field.distribution.dataset.title
    get_dataset_title.short_description = 'Dataset'
    get_dataset_title.admin_order_field = 'distribution__dataset__identifier'

    def get_distribution_title(self, field):
        return field.distribution.title
    get_distribution_title.short_description = 'Distribution'
    get_distribution_title.admin_order_field = 'distribution__title'

    def get_title(self, obj):
        return obj.title or 'No title'
    get_title.short_description = 'Title'

    def get_search_results(self, request, queryset, search_term):
        queryset, distinct = \
            super(FieldAdmin, self).get_search_results(request, queryset, search_term)
        if not search_term:
            return queryset, distinct

        ids_to_remove = []
        for obj in queryset:
            if search_term not in (obj.distribution.identifier,
                                   obj.distribution.dataset.identifier):
                ids_to_remove.append(obj.id)

        return queryset.exclude(id__in=ids_to_remove), distinct


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

    def save_form(self, request, form, change):
        return super(BaseRegisterFileAdmin, self).save_form(request, form, change)


class NodeRegisterFileAdmin(BaseRegisterFileAdmin):

    def process_register_file(self, _, queryset):
        for model in queryset:
            model.state = NodeRegisterFile.state = NodeRegisterFile.PROCESSING
            model.logs = u'-'
            model.save()
            process_node_register_file_action(model)


class InlineNodeMetadata(admin.StackedInline):
    model = NodeMetadata


class NodeAdmin(admin.ModelAdmin):
    list_display = ('catalog_id', 'indexable')
    exclude = ('catalog',)
    inlines = (InlineNodeMetadata,)
    actions = ('run_indexing', 'make_indexable', 'make_unindexable')

    def make_unindexable(self, _, queryset):
        queryset.update(indexable=False)
    make_unindexable.short_description = 'Marcar como no indexable'

    def make_indexable(self, _, queryset):
        queryset.update(indexable=True)
    make_indexable.short_description = 'Marcar como indexable'


class AbstractTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('status', 'created', 'finished', 'logs',)
    list_display = ('__unicode__', 'status')

    change_list_template = 'task_change_list.html'

    # Clase del modelo asociado
    model = None

    # Task (callable) a correr asincrónicamente. Por default recible solo una
    # instancia del AbstractTask asociado a este admin, overridear save_model
    # si se quiere otro comportamiento
    task = None

    # String con el fully qualified name del método a llamar cuando
    # se programa una tarea periódica.
    callable_str = None

    def save_model(self, request, obj, form, change):
        super(AbstractTaskAdmin, self).save_model(request, obj, form, change)
        self.task.delay(obj)  # Ejecuta callable

    def add_view(self, request, form_url='', extra_context=None):
        # Bloqueo la creación de nuevos modelos cuando está corriendo la tarea
        if self.model.objects.filter(status=self.model.RUNNING):
            messages.error(request, "Ya está corriendo una tarea")
            return super(AbstractTaskAdmin, self).changelist_view(request, None)

        return super(AbstractTaskAdmin, self).add_view(request, form_url, extra_context)

    def get_urls(self):
        urls = super(AbstractTaskAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        extra_urls = [url(r'^schedule_task$',
                          self.admin_site.admin_view(self.schedule_task),
                          {'callable_str': self.callable_str},
                          name='%s_%s_schedule_task' % info), ]
        return extra_urls + urls

    def schedule_task(self, request, callable_str):
        form = ScheduleJobForm(initial={'callable': callable_str,
                                        'queue': 'indexing',
                                        'name': self.model._meta.verbose_name_plural})

        context = {
            'title': 'Schedule new task',
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        if request.method == 'POST':
            form = ScheduleJobForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin:scheduler_repeatablejob_changelist')

        if callable_str is not None:
            form.fields['callable'].widget.attrs['readonly'] = True
        form.fields['queue'].widget.attrs['readonly'] = True

        context['adminform'] = helpers.AdminForm(form, list([(None, {'fields': form.base_fields})]),
                                                 self.get_prepopulated_fields(request))
        return render(request, 'scheduler.html', context)


class DataJsonAdmin(AbstractTaskAdmin):
    model = ReadDataJsonTask
    task = read_datajson
    callable_str = 'django_datajsonar.tasks.schedule_new_read_datajson_task'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('indexing_mode',)
        else:
            return self.readonly_fields


class DatasetIndexingFileAdmin(BaseRegisterFileAdmin):
    def process_register_file(self, _, queryset):
        for model in queryset:
            model.state = DatasetIndexingFile.state = DatasetIndexingFile.PROCESSING
            model.logs = u'-'  # Valor default mientras se ejecuta
            model.save()
            bulk_whitelist.delay(model.id)


class CustomRepeatableJobAdmin(RepeatableJobAdmin):

    actions = ['delete_and_unschedule']

    def delete_model(self, request, obj):
        obj.unschedule()
        return super(CustomRepeatableJobAdmin, self).delete_model(request, obj)

    def delete_and_unschedule(self, _, queryset):
        for job in queryset:
            job.unschedule()
        queryset.delete()
    delete_and_unschedule.short_description = 'Delete and unschedule job'

    def get_actions(self, request):
        actions = super(CustomRepeatableJobAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


class SynchronizerAdmin(admin.ModelAdmin):

    change_list_template = 'synchro_change_list.html'

    def get_urls(self):
        urls = super(SynchronizerAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        extra_urls = [url(r'^new_process$',
                          self.admin_site.admin_view(self.new_process),
                          name='%s_%s_new_process' % info), ]
        return extra_urls + urls

    def new_process(self, request):
        synchro_form = SynchroForm()
        stages_form = None

        context = {
            'title': 'Define new process',
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        if request.method == 'POST':
            if 'synchro' in request.POST:
                synchro_form = SynchroForm(request.POST)
                if synchro_form.is_valid():
                    request.session['synchro_name'] = synchro_form.cleaned_data['name']
                    request.session['stages_amount'] = synchro_form.cleaned_data['stages_amount']
                    stages_form = modelformset_factory(Stage, form=StageForm,
                                                       extra=request.session.get('stages_amount', 1),
                                                       formset=StageFormset)()

            elif 'stages' in request.POST:
                synchro_form = SynchroForm({'name': request.session['synchro_name'],
                                            'stages_amount': request.session['stages_amount']})
                stages_form = modelformset_factory(Stage, form=StageForm,
                                                   extra=request.session.get('stages_amount', 1),
                                                   formset=StageFormset)(request.POST)
                if stages_form.is_valid() and synchro_form.is_valid():
                    stages = generate_stages(stages_form)
                    synchro_form.instance.start_stage = stages[0]
                    synchro_form.save()
                    return redirect('admin:django_datajsonar_synchronizer_changelist')

        context['synchro_form'] = helpers.AdminForm(synchro_form, list([(None, {'fields': synchro_form.base_fields})]),
                                                    self.get_prepopulated_fields(request))
        context['stages_form'] = stages_form
        return render(request, 'synchronizer.html', context)


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


admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Distribution, DistributionAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Jurisdiction)

admin.site.register(DatasetIndexingFile, DatasetIndexingFileAdmin)
admin.site.register(NodeRegisterFile, NodeRegisterFileAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(ReadDataJsonTask, DataJsonAdmin)

admin.site.unregister(RepeatableJob)
admin.site.register(RepeatableJob, CustomRepeatableJobAdmin)

admin.site.register(Synchronizer, SynchronizerAdmin)
admin.site.register(Stage)
