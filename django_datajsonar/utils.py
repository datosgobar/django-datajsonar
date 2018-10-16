#!coding=utf8
from __future__ import unicode_literals

from importlib import import_module
import csv

from django.http import HttpResponse
from django.utils.timezone import localtime

from rq.registry import StartedJobRegistry
from django_rq import get_queue, get_connection


def download_config_csv(datasets):
    response = HttpResponse(content_type='text/csv')
    filename = 'config_%s.csv' % localtime().date()
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return generate_csv(datasets, response)


def generate_csv(datasets, output):
    writer = csv.writer(output)
    writer.writerow(['catalog_id', 'dataset_identifier'])
    for dataset in datasets:
        writer.writerow([dataset.catalog.identifier, dataset.identifier])
    return output


def pending_or_running_jobs(queue):
    """
    Chequea si hay trabajos encolados o corriendo, en la cola
    pasada por parámetro
    """
    rq_queue = get_queue(queue)
    pending = bool(rq_queue.jobs)
    registry = StartedJobRegistry(name=queue, connection=get_connection(queue))
    running = bool(len(registry))
    return pending or running


def run_callable(callable_str):
    method = import_string(callable_str)
    return method()


def import_string(string):
    split = string.split('.')
    module = import_module('.'.join(split[:-1]))
    attribute = getattr(module, split[-1], None)
    return attribute


def generate_stages(stages_formset):
    next_stage = None
    for stage_form in stages_formset.forms[::-1]:
        if stage_form.has_changed():
            stage_form.instance.next_stage = next_stage
            stage_form.instance.save()
            next_stage = stage_form.instance

    return [form.instance for form in stages_formset if form.instance]


def get_qualified_name(target_class):
    return target_class.__module__ + '.' + target_class.__name__
