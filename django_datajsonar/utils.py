#!coding=utf8
from __future__ import unicode_literals

import csv


def generate_csv(datasets, output):
    writer = csv.writer(output)
    writer.writerow(['catalog_id', 'dataset_identifier'])
    for dataset in datasets:
        writer.writerow([dataset.catalog.identifier, dataset.identifier])
    return output
