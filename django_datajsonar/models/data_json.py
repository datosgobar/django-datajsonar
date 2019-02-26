#! coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from .metadata import Metadata
from .utils import filepath, get_distribution_storage


class Catalog(models.Model):
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, unique=True)
    metadata = models.TextField()
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata, null=True)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.identifier)

    def __str__(self):
        return self.__unicode__()


class Dataset(models.Model):

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
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)
    indexable = models.BooleanField(default=False)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    reviewed = models.CharField(max_length=20, choices=REVIEWED_STATUS,
                                default=NOT_REVIEWED)
    last_reviewed = models.DateField(null=True, blank=True, default=None)

    themes = models.TextField(blank=True, null=True)

    enhanced_meta = GenericRelation(Metadata)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class Distribution(models.Model):
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    metadata = models.TextField()
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
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class Field(models.Model):
    title = models.CharField(max_length=200, null=True)
    identifier = models.CharField(max_length=200, null=True)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' %\
               (self.title or 'Field sin title',
                self.distribution.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()
