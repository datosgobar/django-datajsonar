#! coding: utf-8
from __future__ import division

import json
from django.conf import settings
from django_rq import job
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from django_datajsonar.models import Dataset, Catalog, Distribution, Field
from django_datajsonar.models import ReadDataJsonTask
from django_datajsonar.models.config import IndexingConfig
from .database_loader import DatabaseLoader
from .strings import READ_ERROR
from .utils import log_exception


class CatalogReader:

    def __init__(self, read_local=False, whitelist=False, indexing_config=None):
        self.read_local = read_local
        self.whitelist = whitelist
        if indexing_config is None:
            indexing_config = IndexingConfig.get_solo()
        self.indexing_config = indexing_config

    def index(self, node, task):
        self._reset_catalog_if_exists(node)

        try:
            catalog = DataJson(node.catalog_url, catalog_format=node.catalog_format)
            catalog.generate_distribution_ids()
            node.catalog = json.dumps(catalog)
            node.save()
        except NonParseableCatalog as e:
            self._set_catalog_as_errored(node)
            ReadDataJsonTask.info(task, READ_ERROR.format(node.catalog_id, e))
            return

        self.reset_fields(node)

        self._index_catalog(catalog, node, task)

    def _index_catalog(self, catalog, node, task):
        verify_ssl = self.indexing_config.verify_ssl
        try:
            loader = DatabaseLoader(task, read_local=self.read_local,
                                    default_whitelist=self.whitelist,
                                    verify_ssl=verify_ssl)
            ReadDataJsonTask.info(task, u"Corriendo loader para catalogo {}".format(node.catalog_id))
            loader.run(catalog, node.catalog_id)
        except Exception as e:
            msg = u"Excepcion en catalogo {}: {}".format(node.catalog_id, e)
            log_exception(task, msg, Catalog, {'identifier': node.catalog_id})

    def reset_fields(self, node):
        fields = {'present': False,
                  'updated': False,
                  'error': False,
                  'error_msg': '',
                  'new': False}
        Dataset.objects.filter(catalog__identifier=node.catalog_id).update(**fields)
        Distribution.objects.filter(dataset__catalog__identifier=node.catalog_id).update(**fields)
        Field.objects.filter(distribution__dataset__catalog__identifier=node.catalog_id).update(**fields)

    def _set_catalog_as_errored(self, node):
        Catalog.objects.filter(identifier=node.catalog_id).update(present=False, error=True)

    def _reset_catalog_if_exists(self, node):
        catalog_model = Catalog.objects.filter(identifier=node.catalog_id)
        # Seteo inicial de variables a usar durante la indexación
        if catalog_model:
            catalog_model[0].updated = False
            catalog_model[0].error = False
            catalog_model[0].save()
        return catalog_model


@job('indexing', timeout=getattr(settings, 'INDEX_CATALOG_TIMEOUT', 1800))
def index_catalog(node, task, read_local=False, whitelist=False):
    CatalogReader(read_local, whitelist).index(node, task)
