#! coding: utf-8
from __future__ import unicode_literals

import json

from django.db import models
from django.utils import timezone

from django_datajsonar.frequency import get_next_run_date
from django_datajsonar.models.node import Node
from django_datajsonar.strings import SYNCHRO_DAILY_FREQUENCY,\
    SYNCHRO_WEEK_DAYS_FREQUENCY
from .stage import Stage


class Synchronizer(models.Model):

    RUNNING = True
    STAND_BY = False

    STATUS_CHOICES = (
        (RUNNING, "Corriendo procesos"),
        (STAND_BY, "En espera"),
    )

    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False, choices=STATUS_CHOICES)

    start_stage = models.ForeignKey(to=Stage, related_name='synchronizer',
                                    on_delete=models.PROTECT)
    actual_stage = models.ForeignKey(to=Stage,
                                     related_name='running_synchronizer',
                                     null=True, blank=True,
                                     on_delete=models.PROTECT)

    node = models.ForeignKey(to=Node, blank=True, null=True)

    WEEK_DAYS = SYNCHRO_WEEK_DAYS_FREQUENCY
    DAILY = SYNCHRO_DAILY_FREQUENCY
    FREQUENCY_CHOICES = (
        (DAILY, 'Every day'),
        (WEEK_DAYS, 'Week days'),
    )
    frequency = models.CharField(choices=FREQUENCY_CHOICES, max_length=16,
                                 default=DAILY)
    scheduled_time = models.TimeField(default=timezone.now)

    last_time_ran = models.DateTimeField(auto_now_add=True)

    week_days = models.TextField(blank=True)

    def begin_stage(self, stage=None):
        if self.status == self.RUNNING and stage is None:
            raise Exception('El synchronizer ya está corriendo,'
                            'pero no se pasó la siguiente etapa.')
        stage = stage or self.start_stage
        self.status = self.RUNNING
        self.actual_stage = stage
        self.last_time_ran = timezone.now()
        self.save()
        stage.open_stage(self.node)

    def check_completion(self):
        if self.status != self.RUNNING:
            raise Exception('El synchronizer no está corriendo')
        return self.actual_stage.check_completion()

    def next_stage(self):
        if self.status != self.RUNNING:
            raise Exception('El synchronizer no está corriendo')
        self.actual_stage.close_stage()
        if self.actual_stage.next_stage is None:
            self.status = self.STAND_BY
            self.actual_stage = None
            self.node = None
            self.save()
        else:
            self.begin_stage(self.actual_stage.next_stage)

    def next_start_date(self):
        start_time = self.last_time_ran\
            .astimezone(timezone.get_current_timezone())
        week_days = self.get_days_of_week()
        return get_next_run_date(start_time, self.scheduled_time,
                                 week_days=week_days)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def get_stages(self):
        stages = []
        current_stage = self.start_stage
        while current_stage is not None:
            stages.append(current_stage)
            current_stage = current_stage.next_stage
        return stages

    def get_days_of_week(self):
        if self.frequency == self.WEEK_DAYS:
            return json.loads(self.week_days)
        return []
