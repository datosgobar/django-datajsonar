#!coding=utf8

from .models import Dataset
from .utils import download_config_csv


def config_csv(_):
    datasets = Dataset.objects.filter(federable=True)
    return download_config_csv(datasets)
