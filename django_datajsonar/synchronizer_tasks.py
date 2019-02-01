#!coding=utf8
from __future__ import unicode_literals

from django.utils import timezone

from .models import Synchronizer


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


def start_synchros():
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.STAND_BY)
    now = timezone.now()
    for synchro in synchronizers:
        if now > synchro.next_start_date():
            synchro.begin_stage()
