#!coding=utf8
from __future__ import unicode_literals

from .models import Synchronizer


def upkeep():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.RUNNING)
    for synchro in synchronizers:
        synchro.check_completion()


def start_synchros():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.STAND_BY)
    synchronizers.update(status=Synchronizer.RUNNING)
    for synchro in synchronizers:
        synchro.begin_stage()
