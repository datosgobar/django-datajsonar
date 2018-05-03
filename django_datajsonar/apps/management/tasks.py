#! coding: utf-8

import logging
import yaml

from django.utils import timezone
from django_rq import job

from django_datajsonar.apps.management.actions import DatasetIndexableToggler
from django_datajsonar.apps.management.models import Node, DatasetIndexingFile, NodeRegisterFile
from django_datajsonar.apps.management.strings import FILE_READ_ERROR
from django_datajsonar.libs.indexing.catalog_reader import index_catalog

logger = logging.getLogger(__name__)


@job('indexing')
def read_datajson(task, whitelist=False, read_local=False):
    """Tarea raíz de indexación. Itera sobre todos los nodos indexables (federados) e
    inicia la tarea de indexación sobre cada uno de ellos
    """
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        try:
            index_catalog(node, task, read_local, whitelist)
        except Exception as e:
            logger.error(u"Excepción en leyendo nodo {}: {}".format(node.id, e.message))


@job('indexing')
def bulk_whitelist(indexing_file_id):
    """Marca datasets como indexables en conjunto a partir de la lectura
    del archivo la instancia del DatasetIndexingFile pasado
    """
    indexing_file_model = DatasetIndexingFile.objects.get(id=indexing_file_id)
    toggler = DatasetIndexableToggler()
    try:
        logs_list = toggler.process(indexing_file_model.indexing_file)
        logs = ''
        for log in logs_list:
            logs += log + '\n'

        state = DatasetIndexingFile.PROCESSED
    except ValueError:
        logs = FILE_READ_ERROR
        state = DatasetIndexingFile.FAILED

    indexing_file_model.state = state
    indexing_file_model.logs = logs
    indexing_file_model.modified = timezone.now()
    indexing_file_model.save()


@job('indexing')
def process_node_register_file(register_file_id):
    register_file = NodeRegisterFile.objects.get(id=register_file_id)

    indexing_file = register_file.indexing_file
    yml = indexing_file.read()
    nodes = yaml.load(yml)
    for node, values in nodes.items():
        try:
            # evitar entrar al branch con un valor truthy
            if bool(values['federado']) is True and values['formato'] == 'json':
                Node.objects.get_or_create(catalog_id=node,
                                        catalog_url=values['url'],
                                        indexable=True)
            register_file.logs = register_file.logs + (
                " - Guardado Node Indexing File %s" % (node, ))    
        except Exception as e:
            register_file.logs = register_file.logs + (
                " - Error guardando Node Indexing File %s - %s" % (node, e))

    register_file.state = NodeRegisterFile.PROCESSED
    register_file.save()