#! coding: utf-8
from __future__ import division

import json
from django.conf import settings
from django_rq import job
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from django_datajsonar.models import Dataset, Catalog, Distribution, Field
from django_datajsonar.models import ReadDataJsonTask, NodeMetadata
from .database_loader import DatabaseLoader
from .strings import READ_ERROR
from .utils import log_exception


@job('indexing', timeout=getattr(settings, 'INDEX_CATALOG_TIMEOUT', 1800))
def index_catalog(node, task, read_local=False, whitelist=False):
    """Ejecuta el pipeline de lectura, guardado e indexado de datos
    y metadatos sobre cada distribución del catálogo especificado

    Args:
        node (Node): Nodo a indexar
        task (ReadDataJsonTask): Task a loggear acciones
        read_local (bool): Lee las rutas a archivos fuente como archivo
        local o como URL. Default False
        whitelist (bool): Marcar los datasets nuevos como federables por defecto. Default False
    """
    catalog_model = Catalog.objects.filter(identifier=node.catalog_id)
    # Seteo inicial de variables a usar durante la indexación
    if catalog_model:
        catalog_model[0].updated = False
        catalog_model[0].error = False
        catalog_model[0].save()

    try:
        catalog = DataJson(node.catalog_url, catalog_format=node.catalog_format)
        catalog.generate_distribution_ids()
        node.catalog = json.dumps(catalog)
        node.save()
    except NonParseableCatalog as e:
        if catalog_model:
            catalog_model[0].present = False
            catalog_model[0].error = True
            catalog_model[0].save()
        ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e))
        return

    reset_fields = {'present': False,
                    'updated': False,
                    'error': False,
                    'error_msg': '',
                    'new': False}

    Dataset.objects.filter(catalog__identifier=node.catalog_id).update(**reset_fields)
    Distribution.objects.filter(dataset__catalog__identifier=node.catalog_id).update(**reset_fields)
    Field.objects.filter(distribution__dataset__catalog__identifier=node.catalog_id).update(**reset_fields)

    try:
        loader = DatabaseLoader(task, read_local=read_local, default_whitelist=whitelist)
        ReadDataJsonTask.info(task, u"Corriendo loader para catalogo {}".format(node.catalog_id))
        loader.run(catalog, node.catalog_id)
    except Exception as e:
        msg = u"Excepcion en catalogo {}: {}".format(node.catalog_id, e)
        log_exception(task, msg, Catalog, {'identifier': node.catalog_id})
        if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            raise e  # Django-rq / sentry logging
