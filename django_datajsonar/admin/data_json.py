from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils import timezone

from django_datajsonar.models import Dataset, Metadata, Catalog, Distribution, Field
from django_datajsonar.utils import download_config_csv
from django_datajsonar.views import config_csv


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


@admin.register(Catalog)
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


@admin.register(Dataset)
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


@admin.register(Distribution)
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

@admin.register(Field)
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
