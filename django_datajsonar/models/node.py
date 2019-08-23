#! coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from pydatajson import DataJson


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

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    indexing_file = models.FileField(upload_to='register_files/')
    uploader = models.ForeignKey(User)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    logs = models.TextField(default=u'-')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.state = self.UPLOADED

        super(BaseRegisterFile, self).save(
            force_insert, force_update, using, update_fields)


class NodeRegisterFile(BaseRegisterFile):
    def __unicode__(self):
        return "Node register file: {}".format(self.created)

    def __str__(self):
        return self.__unicode__()


class DatasetIndexingFile(BaseRegisterFile):
    class Meta:
        verbose_name = 'Dataset federation file'

    def __unicode__(self):
        return "Indexing file: {}".format(self.created)

    def __str__(self):
        return self.__unicode__()


class Jurisdiction(models.Model):
    jurisdiction_title = models.CharField(max_length=100, unique=True)
    jurisdiction_id = models.CharField(max_length=100, unique=True)
    argentinagobar_id = models.CharField(max_length=50, null=True, blank=True)
    modified_date = models.DateField(auto_now=True)

    def __unicode__(self):
        return "%s" % self.jurisdiction_title

    def __str__(self):
        return self.__unicode__()


class Node(models.Model):
    CKAN = "ckan"
    XLSX = "xlsx"
    JSON = "json"
    FORMATS = (
        (CKAN, "Portal CKAN"),
        (XLSX, "Catálogo XLSX"),
        (JSON, "Catálogo JSON"),
    )

    catalog_id = models.CharField(max_length=100, unique=True)
    catalog_url = models.URLField()
    indexable = models.BooleanField(verbose_name='federable')
    catalog = models.TextField(default='{}')
    admins = models.ManyToManyField(User, blank=True)
    catalog_format = models.CharField(max_length=20, choices=FORMATS,
                                      null=True, blank=True)
    register_date = models.DateField(default=timezone.now)
    release_date = models.DateField(null=True, blank=True)

    verify_ssl = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.release_date is None and self.indexable is True:
            self.release_date = timezone.now().date()
        super(Node, self).save(force_insert, force_update, using, update_fields)

    def read_catalog(self):
        return DataJson(self.catalog_url, catalog_format=self.catalog_format)

    def __unicode__(self):
        return self.catalog_id

    def __str__(self):
        return self.__unicode__()


class NodeMetadata(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "Node Metadata"

    CENTRAL = "central"
    NO_CENTRAL = "no-central"
    CATEGORIES = (
        (CENTRAL, "Catálogo central"),
        (NO_CENTRAL, "Catálogo no central")
    )

    ANDINO = "andino"
    EXCEL = "excel"
    OTHER = "other"
    CKAN = "ckan"
    TYPES = (
        (ANDINO, "Andino"),
        (EXCEL, "Excel"),
        (CKAN, "CKAN"),
        (OTHER, "Otros")
    )
    label = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES,
                                null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPES,
                            null=True, blank=True)
    jurisdiction = models.ForeignKey(to=Jurisdiction, null=True,
                                     blank=True, on_delete=models.SET_NULL)
    url_json = models.URLField(null=True, blank=True)
    url_xlsx = models.URLField(null=True, blank=True)
    url_datosgobar = models.URLField(null=True, blank=True)
    url_homepage = models.URLField(null=True, blank=True)
    node = models.OneToOneField(Node, on_delete=models.CASCADE,
                                primary_key=True)
    modified_date = models.DateField(auto_now=True)
