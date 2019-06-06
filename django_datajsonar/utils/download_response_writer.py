#!coding=utf8
from collections import OrderedDict

from django_datajsonar.utils.metadata_generator import \
    get_jurisdiction_list_metadata, get_distributions_metadata


def write_node_metadata(output, fields, writer):
    metadata_list = flatten_jurisdiction_list_metadata(
        get_jurisdiction_list_metadata())
    metadata_list = translate_fields(metadata_list, fields)
    headers = fields.values()
    metadata_writer = writer(output, headers)
    metadata_writer.write_metadata(metadata_list)
    return output


def write_distributions_metadata(output, fields, writer):
    metadata_list = get_distributions_metadata()
    metadata_list = translate_fields(metadata_list, fields)
    headers = fields.values()
    metadata_writer = writer(output, headers)
    metadata_writer.write_metadata(metadata_list)
    return output


def flatten_jurisdiction_list_metadata(jurisdictions):
    result = []
    for jurisdiction in jurisdictions:
        catalogs = jurisdiction.pop('catalogs')
        for catalog in catalogs:
            catalog.update(jurisdiction)
            result.append(catalog)
    return result


def translate_fields(metadata_list, fields_translation):
    return [OrderedDict(
        {fields_translation[key]: catalog[key]for key in fields_translation})
        for catalog in metadata_list]
