#!coding=utf8
from django.http import JsonResponse

from django_datajsonar.models.data_json import Dataset
from django_datajsonar.utils.metadata_generator import project_metadata, \
    jurisdiction_list_metadata
from django_datajsonar.utils.utils import download_config_csv


def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)


def nodes_metadata_json(_):
    response = {'meta': project_metadata(),
                'jurisdictions': jurisdiction_list_metadata()}
    return JsonResponse(response)
