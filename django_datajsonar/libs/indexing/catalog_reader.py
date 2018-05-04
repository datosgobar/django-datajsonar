#! coding: utf-8
from __future__ import division

import json
from django.conf import settings
from django.db.models import Q
from django_rq import job
from pydatajson import DataJson

from django_datajsonar.apps.api.models import Dataset, Catalog, Distribution, Field
from django_datajsonar.apps.management.models import ReadDataJsonTask
from .database_loader import DatabaseLoader
from .strings import READ_ERROR


@job('indexing')
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
        loader = DatabaseLoader(task, read_local=read_local, default_whitelist=whitelist)
        ReadDataJsonTask.info(task, u"Corriendo loader para catalogo {}".format(node.catalog_id))
        loader.run(catalog, node.catalog_id)
    except Exception as e:
        ReadDataJsonTask.info(task, u"Excepcion en catalogo {}: {}".format(node.catalog_id, e))
        if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            raise e  # Django-rq / sentry logging
