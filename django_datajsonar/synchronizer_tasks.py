#!coding=utf8
from __future__ import unicode_literals

from .models import Synchronizer


def upkeep():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.RUNNING)
    for synchro in synchronizers:
        finished = synchro.check_completion()
        if finished:
            synchro.status = synchro.STAND_BY
            synchro.actual_stage = None
            synchro.save()


def start_synchros():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.STAND_BY)
    for synchro in synchronizers:
        synchro.begin_stage()
    # Refresh queryset
    synchronizers.all()
    synchronizers.update(status=Synchronizer.RUNNING)
