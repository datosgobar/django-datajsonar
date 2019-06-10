#!coding=utf8
from __future__ import unicode_literals

import json

from django.forms.models import model_to_dict
from django.db.models import Max

from django_datajsonar.models import Distribution
from django_datajsonar.models.metadata import ProjectMetadata, Language,\
    Spatial, Publisher
from django_datajsonar.models.node import Jurisdiction, NodeMetadata


def get_project_metadata():
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


def get_jurisdiction_list_metadata():
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


def get_distributions_metadata():
    metadata_list = list(Distribution.objects.all().select_related('dataset__catalog').values(
        'identifier',
        'title',
        'download_url',
        'metadata',
        'dataset__identifier',
        'dataset__title',
        'dataset__metadata',
        'dataset__catalog__title',
        'dataset__catalog__identifier',
        'dataset__catalog__metadata'
    ))

    for distribution in metadata_list:
        distribution_metadata = json.loads(distribution.pop('metadata')) \
            if distribution.get('metadata') else {}
        distribution['description'] = distribution_metadata.get('description')
        distribution['accessURL'] = distribution_metadata.get('accessURL')
        distribution['type'] = distribution_metadata.get('type')
        distribution['format'] = distribution_metadata.get('format')

        dataset_metadata = json.loads(distribution.pop('dataset__metadata')) \
            if distribution.get('dataset__metadata') else {}
        distribution['dataset_description'] = \
            dataset_metadata.get('description')
        distribution['dataset_publisher'] = \
            dataset_metadata.get('publisher', {}).get('name')
        distribution['dataset_publisher_mail'] = \
            dataset_metadata.get('publisher', {}).get('mbox')
        distribution['dataset_source'] = \
            dataset_metadata.get('source')
        distribution['dataset_theme'] = \
            ','.join(dataset_metadata.get('theme', []))
        distribution['dataset_superTheme'] = \
            ','.join(dataset_metadata.get('superTheme', []))
        distribution['dataset_license'] = \
            dataset_metadata.get('license')

        catalog_metadata = \
            json.loads(distribution.pop('dataset__catalog__metadata')) \
            if distribution.get('dataset__catalog__metadata') else {}
        distribution['catalog_publisher'] = \
            catalog_metadata.get('publisher', {}).get('name')

    return metadata_list
