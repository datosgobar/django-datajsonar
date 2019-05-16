#!coding=utf8
from django.http import JsonResponse

from django_datajsonar.models.data_json import Dataset
from django_datajsonar.utils.metadata_csv_writer import \
    write_node_metadata_csv
from django_datajsonar.utils.metadata_generator import get_project_metadata, \
    get_jurisdiction_list_metadata
from django_datajsonar.utils.utils import download_config_csv, generate_csv_download_response
from django_datajsonar.utils.translations import ENGLISH_FIELDS, SPANISH_FIELDS


def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)


def nodes_metadata_json(_):
    response = {'meta': get_project_metadata(),
                'jurisdictions': get_jurisdiction_list_metadata()}
    return JsonResponse(response)


def nodes_english_metadata_csv(_):
    response = generate_csv_download_response('nodes.csv')
    return write_node_metadata_csv(response, ENGLISH_FIELDS)


def nodes_spanish_metadata_csv(_):
    response = generate_csv_download_response('nodos.csv')
    return write_node_metadata_csv(response, SPANISH_FIELDS)
