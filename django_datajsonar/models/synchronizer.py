#! coding: utf-8
from __future__ import unicode_literals

import json

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils import timezone

from django_datajsonar.frequency import get_next_run_date
from django_datajsonar.strings import SYNCHRO_DAILY_FREQUENCY,\
    SYNCHRO_WEEK_DAYS_FREQUENCY
from django_datajsonar.utils import pending_or_running_jobs, import_string

from .tasks import AbstractTask


class Stage(models.Model):

    ACTIVE = True
    INACTIVE = False

    STATUS_CHOICES = (
        (ACTIVE, "Tarea activa"),
        (INACTIVE, "Tarea inactiva"),
    )

    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False, choices=STATUS_CHOICES)
    callable_str = models.CharField(max_length=100)
    queue = models.CharField(max_length=50)
    next_stage = models.ForeignKey('self', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    task = models.CharField(max_length=200, blank=True)

    def get_running_task(self):
        if self.task:
            task_model = import_string(self.task)
        else:
            return None
        try:
            return task_model.objects\
                .filter(status=task_model.RUNNING).latest('created')
        except task_model.DoesNotExist:
            return None

    def open_stage(self):
        job = import_string(self.callable_str)
        job.delay()
        self.status = Stage.ACTIVE
        self.save()

    def close_stage(self):
        task = self.get_running_task()
        if task:
            # Cierra la tarea si quedó abierta
            task.status = task.FINISHED
            task.save()
        self.status = self.INACTIVE
        self.save()

    def check_completion(self):
        return not pending_or_running_jobs(self.queue)

    def clean(self):
        errors = {}
        try:
            method = import_string(self.callable_str)
            if not callable(method):
                msg = 'callable_str must be callable: {}'\
                    .format(self.callable_str)
                errors.update({'callable_str': ValidationError(msg)})

            if not hasattr(method, 'delay'):
                msg = 'method referenced is not an rq job ' \
                      '(has no "delay" attribute: {}'.format(self.callable_str)
                errors.update({'callable_str': msg})

        except (ImportError, ValueError):
            msg = 'Unable to import callable_str: {}'.format(self.callable_str)
            errors.update({'callable_str': ValidationError(msg)})

        if self.queue not in settings.RQ_QUEUES:
            msg = 'Queue is not defined in settings: {}'.format(self.queue)
            errors.update({'queue': ValidationError(msg)})

        if self.task:
            try:
                task_model = import_string(self.task)
                if not issubclass(task_model, AbstractTask):
                    msg = 'task must be an AbstractTask subclass: {}'\
                        .format(self.task)
                    errors.update({'task': ValidationError(msg)})
            except (ImportError, TypeError, ValueError):
                errors.update({'task': ValidationError(
                    'If present, task must be importable')})

        if self.next_stage and self.pk and self.next_stage.pk == self.pk:
            msg = 'next_stage must point to a different_stage: {}'.format(self)
            errors.update({'next_stage': ValidationError(msg)})

        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(Stage, self).save(force_insert=False, force_update=False,
                                using=None, update_fields=None)

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.queue)

    def __str__(self):
        return self.__unicode__()


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
        stage.open_stage()

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
