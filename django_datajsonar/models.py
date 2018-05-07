#! coding: utf-8
from __future__ import unicode_literals

import requests

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Metadata(models.Model):
    key = models.CharField(max_length=64)
    value = models.TextField()

    # Generic foreign key magics
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class Catalog(models.Model):
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, unique=True)
    metadata = models.TextField()
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.identifier)


class Dataset(models.Model):
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)
    indexable = models.BooleanField(default=False)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.catalog.identifier)


def filepath(instance, _):
    """Método para asignar el nombre al archivo fuente del FileField
    del modelo Distribution
    """
    return u'distribution_raw/{}.csv'.format(instance.identifier)


class Distribution(models.Model):
    identifier = models.CharField(max_length=200)
    metadata = models.TextField()
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField(max_length=1024)
    data_hash = models.CharField(max_length=128, default='')
    last_updated = models.DateTimeField(blank=True, null=True)
    data_file = models.FileField(
        max_length=2000,
        upload_to=filepath,
        blank=True
    )
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)


class Field(models.Model):
    title = models.CharField(max_length=200, null=True)
    identifier = models.CharField(max_length=200, null=True)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)


class BaseRegisterFile(models.Model):
    """Base de los archivos de registro de datasets y de nodos.
    Contiene atributos de estado del archivo y fechas de creado / modificado
    """
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

    STATE_CHOICES = (
        (UPLOADED, "Cargado"),
        (PROCESSING, "Procesando"),
        (PROCESSED, "Procesado"),
        (FAILED, "Error"),
    )

    created = models.DateTimeField()
    modified = models.DateTimeField(null=True)
    indexing_file = models.FileField(upload_to='register_files/')
    uploader = models.ForeignKey(User)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    logs = models.TextField(default=u'-')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.created = timezone.now()
            self.state = self.UPLOADED

        super(BaseRegisterFile, self).save(force_insert, force_update, using, update_fields)


class NodeRegisterFile(BaseRegisterFile):
    def __unicode__(self):
        return "Node register file: {}".format(self.created)


class DatasetIndexingFile(BaseRegisterFile):
    def __unicode__(self):
        return "Indexing file: {}".format(self.created)


class Node(models.Model):

    catalog_id = models.CharField(max_length=100, unique=True)
    catalog_url = models.URLField()
    indexable = models.BooleanField()
    catalog = models.TextField(default='{}')

    def __unicode__(self):
        return self.catalog_id

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            catalog_request = requests.get(self.catalog_url)
            if catalog_request.status_code != 200:
                return
            self.catalog = catalog_request.content
        except requests.exceptions.RequestException:
            self.catalog = open(self.catalog_url).read()

        super(Node, self).save(force_insert, force_update, using, update_fields)


class ReadDataJsonTask(models.Model):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    RUNNING = "RUNNING"
    INDEXING = "INDEXING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"

    STATUS_CHOICES = (
        (RUNNING, "Procesando catálogos"),
        (INDEXING, "Indexando series"),
        (FINISHED, "Finalizada"),
        (ERROR, "Error"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField()
    finished = models.DateTimeField(null=True)
    logs = models.TextField(default='-')
    catalogs = models.ManyToManyField(to=Node, blank=True)

    stats = models.TextField(default='{}')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.created = timezone.now()
            self.status = self.RUNNING

        super(ReadDataJsonTask, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return "Task at %s" % self._format_date(self.created)

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @classmethod
    def info(cls, task, msg):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            task.logs += msg + '\n'
            task.save()
