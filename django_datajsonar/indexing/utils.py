#! coding: utf-8
import json
from django_datajsonar.models import ReadDataJsonTask


def log_exception(task, msg, model, field_kw):
    ReadDataJsonTask.info(task, msg)
    try:
        error_model = model.objects.get(**field_kw)
        error_model.error = True
        error_model.error_msg = msg
        error_model.save()
        return error_model
    except model.DoesNotExist:
        return None


def update_model(trimmed_dict, model, updated_children=False, data_change=False):
    model.update_metadata(trimmed_dict, updated_children, data_change)
    model.save()
