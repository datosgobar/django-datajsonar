#! coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from django_datajsonar.models.data_json_entity_mixin import DataJsonEntityMixin
from .metadata import Metadata
from .utils import filepath, get_distribution_storage


class Catalog(DataJsonEntityMixin):
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, unique=True)
    enhanced_meta = GenericRelation(Metadata, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.identifier)

    def __str__(self):
        return self.__unicode__()


class Dataset(DataJsonEntityMixin):

    REVIEWED = "REVIEWED"
    ON_REVISION = "ON_REVISION"
    NOT_REVIEWED = "NOT_REVIEWED"

    REVIEWED_STATUS = (
        (REVIEWED, "Revisado"),
        (ON_REVISION, "En revisión"),
        (NOT_REVIEWED, "No revisado"),
    )

    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)
    landing_page = models.URLField(blank=True, null=True)
    indexable = models.BooleanField(default=False, verbose_name='federable')
    time_created = models.DateTimeField(auto_now_add=True)
    starred = models.BooleanField(default=False)
    reviewed = models.CharField(max_length=20, choices=REVIEWED_STATUS,
                                default=NOT_REVIEWED)
    last_reviewed = models.DateField(null=True, blank=True, default=None)

    themes = models.TextField(blank=True, null=True)

    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class Distribution(DataJsonEntityMixin):
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField(max_length=1024, null=True)
    data_hash = models.CharField(max_length=128, default='')
    last_updated = models.DateTimeField(blank=True, null=True)

    data_file = models.FileField(
        storage=get_distribution_storage(),
        max_length=2000,
        upload_to=filepath,
        blank=True
    )
    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class Field(DataJsonEntityMixin):
    title = models.CharField(max_length=200, null=True)
    identifier = models.CharField(max_length=200, null=True)
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)

    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' %\
               (self.title or 'Field sin title',
                self.distribution.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()
