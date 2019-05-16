#!coding=utf8
import csv

from django_datajsonar.utils.metadata_generator import \
    get_jurisdiction_list_metadata


def write_node_metadata_csv(output, fields):
    metadata_list = flatten_jurisdiction_list_metadata(
        get_jurisdiction_list_metadata())
    metadata_list = translate_fields(metadata_list, fields)
    headers = fields.values()
    writer = csv.DictWriter(output, headers, extrasaction='ignore')
    writer.writeheader()
    for catalog in metadata_list:
        writer.writerow(catalog)
    return output


def flatten_jurisdiction_list_metadata(jurisdictions):
    result = []
    for jurisdiction in jurisdictions:
        catalogs = jurisdiction.pop('catalogs')
        for catalog in catalogs:
            catalog.update(jurisdiction)
    return result


def translate_fields(metadata_list, fields_translation):
    return [{fields_translation[key]: catalog[key]for key in fields_translation}
            for catalog in metadata_list]
