#! coding: utf-8
import json

from django.conf import settings
from django_rq import job, get_queue
from pydatajson import DataJson

from django_datajsonar.apps.management.models import ReadDataJsonTask, Node
from django_datajsonar.apps.api.models import Dataset, Catalog
from .database_loader import DatabaseLoader


@job('indexing', timeout=settings.DISTRIBUTION_INDEX_JOB_TIMEOUT)
def index_distribution(dataset_identifier, distribution_id, node_id,
                       task, read_local=False, whitelist=False):

    node = Node.objects.get(id=node_id)
    catalog = DataJson(json.loads(node.catalog))

    distribution = catalog.get_distribution(identifier=distribution_id)
    dataset_model = get_dataset(catalog, node.catalog_id, dataset_identifier, whitelist)
    if not dataset_model.indexable:
        return

    try:
        loader = DatabaseLoader(task, read_local=read_local, default_whitelist=whitelist)

        distribution_model = loader.run(distribution, catalog, node.catalog_id)
        if not distribution_model:
            return

    except Exception as e:
        ReadDataJsonTask.info(task, u"Excepción en distrbución {}: {}".format(distribution_id, e.message))
        if settings.RQ_QUEUES['indexing'].get('ASYNC', True):
            raise e  # Django-rq / sentry logging


def get_dataset(catalog, catalog_id, dataset_id, whitelist):
    catalog_model, created = Catalog.objects.get_or_create(identifier=catalog_id)
    if created:
        catalog_model.title = catalog['title']
        catalog_model.identifier = catalog_id
        catalog_model.save()

    dataset_model, created = Dataset.objects.get_or_create(
        identifier=dataset_id,
        catalog=catalog_model,
    )
    if created:
        dataset_model.indexable = whitelist
        dataset_model.metadata = '{}'

    dataset_model.present = True
    dataset_model.save()
    return dataset_model


# Para correr con el scheduler
def close_read_datajson_task():
    task = ReadDataJsonTask.objects.last()
    if task.status == task.FINISHED:
        return

    if not get_queue('indexing').jobs:
        task.status = task.FINISHED
        task.save()


def schedule_new_read_datajson_task():
    try:
        task = ReadDataJsonTask.objects.last()
        if task.status in [ReadDataJsonTask.INDEXING, ReadDataJsonTask.RUNNING]:
            return
    except ReadDataJsonTask.DoesNotExist:
        pass

    new_task = ReadDataJsonTask()
    new_task.save()
