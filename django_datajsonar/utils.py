#!coding=utf8
from __future__ import unicode_literals

import csv


from django.http import HttpResponse
from django.utils.timezone import now


def download_config_csv(datasets):
    response = HttpResponse(content_type='text/csv')
    filename = 'config_%s.csv' % now().strftime("%Y-%m-%d_%H:%M:%S")
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return generate_csv(datasets, response)


def generate_csv(datasets, output):
    writer = csv.writer(output)
    writer.writerow(['catalog_id', 'dataset_identifier'])
    for dataset in datasets:
        writer.writerow([dataset.catalog.identifier, dataset.identifier])
    return output
