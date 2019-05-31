#!coding=utf8
from __future__ import unicode_literals

from importlib import import_module
import csv

from django.http import HttpResponse
from django.utils.timezone import localtime

from rq.registry import StartedJobRegistry
from django_rq import get_queue, get_connection


def download_config_csv(datasets):
    filename = 'config_%s.csv' % localtime().date()
    response = generate_csv_download_response(filename)
    return generate_csv(datasets, response)


def generate_csv_download_response(filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


def generate_xlsx_download_response(filename):
    response = HttpResponse(content_type='application/'
                                         'vnd.openxmlformats-officedocument.'
                                         'spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


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


def generate_stages(forms, name_prefix):
    next_stage = None
    stages = []
    repeated_names = {}
    for stage_form in forms:
        task = stage_form.cleaned_data['task']
        base_name = '{}: {}'.format(name_prefix, task)
        name = base_name
        if base_name in repeated_names.keys():
            name += ' ({})'.format(repeated_names.get(name))

        repeated_names[base_name] = repeated_names.setdefault(base_name, 1) + 1
        stage = stage_form.get_stage(name)
        stages.append(stage)

    for stage in stages[::-1]:
        stage.next_stage = next_stage
        stage.save()
        next_stage = stage

    return stages


def get_qualified_name(target_class):
    return target_class.__module__ + '.' + target_class.__name__
