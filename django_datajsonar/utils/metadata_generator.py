#!coding=utf8
from django.forms.models import model_to_dict
from django.db.models import Max

from django_datajsonar.models.metadata import ProjectMetadata, Language,\
    Spatial, Publisher
from django_datajsonar.models.node import Jurisdiction, NodeMetadata


def project_metadata():
    metadata = ProjectMetadata.get_solo()
    result = model_to_dict(metadata, fields=[
        'title', 'description', 'version', 'homepage', 'issued'
    ])

    languages = metadata.language_set.all().values_list('language', flat=True)
    result['language'] = list(languages)

    spatial_info = metadata.spatial_set.all().values_list('spatial', flat=True)
    result['spatial'] = list(spatial_info)

    publisher = model_to_dict(Publisher.get_solo(), fields=['name', 'mbox'])
    result['publisher'] = publisher

    result['modified'] = last_modified_date()
    result['jurisdiction_count'] = Jurisdiction.objects.all().count()
    result['catalog_count'] = \
        NodeMetadata.objects.all().exclude(jurisdiction__isnull=True).count()

    return result


def last_modified_date():
    result = ProjectMetadata.get_solo().modified_date
    models = [Jurisdiction, NodeMetadata, Spatial, Publisher, Language]
    for model in models:
        model_last_modified = model.objects.all().aggregate(
            Max('modified_date'))['modified_date__max']
        if model_last_modified:
            result = max(result, model_last_modified)
    return result


def jurisdiction_list_metadata():
    jurisdictions = []
    jurisdictions_models = Jurisdiction.objects.all()
    for jurisdiction_model in jurisdictions_models:
        jurisdictions.append(jurisdiction_metadata(jurisdiction_model))
    return jurisdictions


def jurisdiction_metadata(jurisdiction):
    nodes_metadata = list(jurisdiction.nodemetadata_set.values(
        'node__catalog_id',
        'label',
        'category',
        'type',
        'node__indexable',
        'url_json',
        'url_xlsx',
        'url_datosgobar',
        'url_homepage'
    ))
    for metadata in nodes_metadata:
        # Traducción de campos
        metadata['id'] = metadata.pop('node__catalog_id')
        metadata['published'] = metadata.pop('node__indexable')

    result = {
        "argentinagobar_id": jurisdiction.argentinagobar_id,
        "title": jurisdiction.jurisdiction_title,
        'catalogs': nodes_metadata,
    }
    return result
