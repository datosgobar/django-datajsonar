#!coding=utf8
from django.http import JsonResponse

from django_datajsonar.models.data_json import Dataset
from django_datajsonar.utils.metadata_generator import get_project_metadata, \
    get_jurisdiction_list_metadata
from django_datajsonar.utils.utils import download_config_csv


def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)


def nodes_metadata_json(_):
    response = {'meta': get_project_metadata(),
                'jurisdictions': get_jurisdiction_list_metadata()}
    return JsonResponse(response)
