#! coding: utf-8
from ..models import ReadDataJsonTask


def log_exception(task, msg, model, identifier):
    ReadDataJsonTask.info(task, msg)
    try:
        error_model = model.objects.get(identifier=identifier)
        error_model.error = msg
        error_model.save()
        return error_model
    except model.DoesNotExist:
        return None
