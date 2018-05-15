#! coding: utf-8
import json
from django_datajsonar.models import ReadDataJsonTask


def log_exception(task, msg, model, identifier):
    ReadDataJsonTask.info(task, msg)
    try:
        error_model = model.objects.get(identifier=identifier)
        error_model.error = True
        error_model.save()
        return error_model
    except model.DoesNotExist:
        return None


def update_model(created, trimmed_dict, model, updated_children=False, data_change=False):
    try:
        previous_meta = json.loads(model.metadata)
    except ValueError:
        previous_meta = {}
    updated = (trimmed_dict != previous_meta or data_change or updated_children)
    if created or updated:
        model.metadata = json.dumps(trimmed_dict)
        model.updated = True
    model.new = created
    model.present = True
    model.save()
    return
