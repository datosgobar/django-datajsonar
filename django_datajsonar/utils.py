#!coding=utf8
from __future__ import unicode_literals

from importlib import import_module
import csv

from django.http import HttpResponse
from django.utils.timezone import now

from rq.registry import StartedJobRegistry
from django_rq import get_queue, get_connection


def download_config_csv(datasets):
    response = HttpResponse(content_type='text/csv')
    filename = 'config_%s.csv' % now().date()
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return generate_csv(datasets, response)


def generate_csv(datasets, output):
    writer = csv.writer(output)
    writer.writerow(['catalog_id', 'dataset_identifier'])
    for dataset in datasets:
        writer.writerow([dataset.catalog.identifier, dataset.identifier])
    return output


def pending_or_running_jobs(queue):
    rq_queue = get_queue(queue)
    pending = bool(rq_queue.jobs)
    registry = StartedJobRegistry(name=queue, connection=get_connection(queue))
    running = bool(len(registry))
    return pending or running


def import_string(string):
    split = string.split('.')
    module = import_module('.'.join(split[:-1]))
    attribute = getattr(module, split[-1], None)
    return attribute
