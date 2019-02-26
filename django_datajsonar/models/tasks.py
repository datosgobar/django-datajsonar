#! coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


class AbstractTask(models.Model):

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"

    STATUS_CHOICES = (
        (RUNNING, "Procesando catálogos"),
        (FINISHED, "Finalizada"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    logs = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.status = self.RUNNING

        super(AbstractTask, self).save(force_insert, force_update,
                                       using, update_fields)

    def __unicode__(self):
        return "Task at %s" % self._format_date(self.created)

    def __str__(self):
        return self.__unicode__()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @classmethod
    def info(cls, task, msg):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            task.logs += msg + '\n'
            task.save()

    class Meta:
        abstract = True


class ReadDataJsonTask(AbstractTask):
    class Meta:
        verbose_name = 'Node read task'

    COMPLETE_RUN = True
    METADATA_ONLY = False
    INDEXING_CHOICES = (
        (COMPLETE_RUN, 'Corrida completa'),
        (METADATA_ONLY, 'Corrida solo de metadatos'),
    )
    default_mode = getattr(settings, 'DATAJSON_AR_DOWNLOAD_RESOURCES', True)
    indexing_mode = models.BooleanField(choices=INDEXING_CHOICES,
                                        default=default_mode)
