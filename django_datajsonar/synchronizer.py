#!coding=utf8
from __future__ import unicode_literals

from django.conf import settings
from django.utils import timezone

from django_datajsonar.task_closer import TaskCloser
from django_datajsonar.utils.utils import import_string
from .models import Synchronizer, Stage


def upkeep():
    """"
    Función periódica que chequea la finzalización de cada etapa. En caso de
    que finalice,arranca la siguiente etapa o termina el proceso general.
    """
    start_synchros()

    synchronizers = Synchronizer.objects.filter(status=Synchronizer.RUNNING)
    for synchro in synchronizers:
        if synchro.check_completion():
            synchro.next_stage()

    task_closer = TaskCloser()
    for stage_settings in settings.DATAJSONAR_STAGES.values():
        task = import_string(stage_settings['task'])
        task_closer.close_all_opened(task)


def start_synchros():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.STAND_BY)
    now = timezone.now()
    for synchro in synchronizers:
        if now > synchro.next_start_date():
            synchro.begin_stage()


def create_or_update_synchro(synchro_id, stages, data=None):
    if data is None:
        data = {}

    if synchro_id is None:
        return Synchronizer.objects.create(start_stage=stages[0], **data)

    synchro_queryset = Synchronizer.objects.filter(id=synchro_id)
    synchro_queryset.update(start_stage=stages[0], **data)

    synchro = synchro_queryset.first()
    old_stages = synchro.get_stages()

    Stage.objects \
        .filter(id__in=[stage.id for stage in old_stages]) \
        .exclude(id__in=[stage.id for stage in stages]) \
        .delete()

    synchro.refresh_from_db()
    return synchro
