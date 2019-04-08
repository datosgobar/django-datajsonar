#! coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_datajsonar.models import AbstractTask
from django_datajsonar.utils.utils import import_string, pending_or_running_jobs


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

    def open_stage(self, node=None):
        job = import_string(self.callable_str)
        job.delay(node)
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
