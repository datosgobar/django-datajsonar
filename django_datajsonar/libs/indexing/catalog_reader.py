#! coding: utf-8
from __future__ import division

import json

from django.conf import settings
from django.db.models import Q
from pydatajson import DataJson

from django_datajsonar.apps.api.models import Dataset, Catalog, Distribution, Field
from django_datajsonar.apps.management.models import ReadDataJsonTask
from django_datajsonar.libs.indexing.tasks import index_distribution
from .strings import READ_ERROR


def index_catalog(node, task, read_local=False, whitelist=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        node (Node): Nodo a indexar
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        whitelist (bool): Marcar los datasets nuevos como indexables por defecto. Default False
    """

    try:
        catalog = DataJson(node.catalog_url)
        catalog.generate_distribution_ids()
        node.catalog = json.dumps(catalog)
        node.save()
    except Exception as e:
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e.message))
        return

    # Seteo inicial de variables a usar durante la indexación
    catalog_model = Catalog.objects.filter(identifier=node.catalog_id)
    if catalog_model:
        catalog_model[0].updated = False
        catalog_model[0].save()

    Dataset.objects.filter(catalog__identifier=node.catalog_id).update(present=False, updated=False)
    # Borro de la lista de indexables a los datasets que ya no están presentes en el catálogo
    dataset_ids = [dataset['identifier'] for dataset in catalog.get_datasets()]
    Dataset.objects.filter(~Q(identifier__in=dataset_ids), catalog__identifier=node.catalog_id).update(indexable=False)

    Distribution.objects.filter(dataset__catalog__identifier=node.catalog_id).update(updated=False)
    Field.objects.filter(distribution__dataset__catalog=catalog_model).update(updated=False)

    try:
        only_time_series = settings.DATAJSON_AR_TIME_SERIES_ONLY
    except AttributeError:
        only_time_series = False
    datasets = catalog.get_datasets(only_time_series=only_time_series)
    for dataset in datasets:
        for distribution in dataset['distribution']:
            dataset_identifier = dataset['identifier']
            distribution_identifier = distribution['identifier']
            index_distribution.delay(dataset_identifier, distribution_identifier,
                                     node.id, task, read_local, whitelist)

    if not datasets and only_time_series:
        msg = "No fueron encontrados series de tiempo en el catálogo {}".format(node.catalog_id)
        ReadDataJsonTask.info(task, msg)
