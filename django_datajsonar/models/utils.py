#! coding: utf-8
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.core.files.storage import default_storage


def filepath(instance, _):
    """Método para asignar el nombre al archivo fuente del FileField
    del modelo Distribution
    """
    return u'distribution_raw/{}/{}.csv'.format(
        instance.dataset.catalog.identifier, instance.identifier)


def get_distribution_storage():
    """Importa dinámicamente el módulo configurado en el setting
    DATAJSON_AR_DISTRIBUTION_STORAGE, y devuelve una instancia
    del objeto determinado. De no existir, devuelve el storage default
    """
    data_file_storage_path = getattr(
        settings, 'DATAJSON_AR_DISTRIBUTION_STORAGE', None)
    if data_file_storage_path is None:
        return default_storage

    split = data_file_storage_path.split('.')
    module = import_module('.'.join(split[:-1]))

    storage = getattr(module, split[-1], None)
    if storage is None:
        raise ImproperlyConfigured

    return storage()
