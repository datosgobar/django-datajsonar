#! coding: utf-8
from django.conf import settings

IDENTIFIER = "identifier"
DATASET_IDENTIFIER = "dataset_identifier"
DOWNLOAD_URL = "downloadURL"
TITLE = 'title'

DATASET = 'dataset'
DISTRIBUTION = 'distribution'
FIELD = 'field'
FIELD_TITLE = 'title'
FIELD_ID = 'id'
FIELD_DESCRIPTION = 'description'
SPECIAL_TYPE = 'specialType'
SPECIAL_TYPE_DETAIL = 'specialTypeDetail'
TIME_INDEX = 'time_index'


FORCE_MERGE_SEGMENTS = 5

REQUEST_TIMEOUT = 30  # en segundos

DEACTIVATE_REFRESH_BODY = {
    'index': {
        'refresh_interval': -1
    }
}

REACTIVATE_REFRESH_BODY = {
    'index': {
        'refresh_interval': "30s"
    }
}

CATALOG_ROOT = 'catalog'