#!coding=utf8
from django.http import JsonResponse

from django_datajsonar.models.data_json import Dataset
from django_datajsonar.utils.download_response_writer import \
    write_node_metadata, write_distributions_metadata
from django_datajsonar.utils.metadata_generator import get_project_metadata, \
    get_jurisdiction_list_metadata
from django_datajsonar.utils.metadata_writer import CSVMetadataWriter, \
    XLSXMetadataWriter
from django_datajsonar.utils.utils import download_config_csv, \
    generate_csv_download_response, generate_xlsx_download_response
from django_datajsonar.utils.translations import NODES_ENGLISH_FIELDS, NODES_SPANISH_FIELDS, \
    DISTRIBUTIONS_SPANISH_FIELDS


def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)


def nodes_metadata_json(_):
    response = {'meta': get_project_metadata(),
                'jurisdictions': get_jurisdiction_list_metadata()}
    return JsonResponse(response)


def nodes_english_metadata_csv(_):
    response = generate_csv_download_response('nodes.csv')
    return write_node_metadata(response, NODES_ENGLISH_FIELDS,
                               CSVMetadataWriter)


def nodes_spanish_metadata_csv(_):
    response = generate_csv_download_response('nodos.csv')
    return write_node_metadata(response, NODES_SPANISH_FIELDS,
                               CSVMetadataWriter)


def nodes_english_metadata_xlsx(_):
    response = generate_xlsx_download_response('nodes.xlsx')
    return write_node_metadata(response, NODES_ENGLISH_FIELDS,
                               XLSXMetadataWriter)


def nodes_spanish_metadata_xlsx(_):
    response = generate_xlsx_download_response('nodos.xlsx')
    return write_node_metadata(response, NODES_SPANISH_FIELDS,
                               XLSXMetadataWriter)


def distributions_spanish_metadata_csv(_):
    response = generate_csv_download_response('distribuciones.csv')
    return write_distributions_metadata(response, DISTRIBUTIONS_SPANISH_FIELDS,
                                        CSVMetadataWriter)


def distributions_spanish_metadata_xlsx(_):
    response = generate_xlsx_download_response('distribuciones.xlsx')
    return write_distributions_metadata(response, DISTRIBUTIONS_SPANISH_FIELDS,
                                        XLSXMetadataWriter)
