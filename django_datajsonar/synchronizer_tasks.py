#!coding=utf8
from __future__ import unicode_literals

from .models import Synchronizer


def upkeep():
    """"
    Función periódica que chequea la finzalización de cada etapa. En caso de
    que finalice,arranca la siguiente etapa o termina el proceso general.
    """
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.RUNNING)
    for synchro in synchronizers:
        if synchro.check_completion():
            synchro.next_stage()


def start_synchros():
    """"
    Función periódica que comienza todos los procesos que se encuentran en espera.
    """
    synchronizers = Synchronizer.objects.filter(status=Synchronizer.STAND_BY)
    for synchro in synchronizers:
        synchro.begin_stage()
    # Refresh queryset
    synchronizers.all()
    synchronizers.update(status=Synchronizer.RUNNING)
