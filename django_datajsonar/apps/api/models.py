#! coding: utf-8
from django.db import models

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
    updated = models.BooleanField(default=False)

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
    updated = models.BooleanField(default=False)

    data_file = models.FileField(
        max_length=2000,
        upload_to=filepath,
        blank=True
    )

    data_hash = models.CharField(max_length=128, default='')
    last_updated = models.DateTimeField(blank=True, null=True)
    indexable = models.BooleanField(default=False)
    enhanced_meta = GenericRelation(Metadata)

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)


class Field(models.Model):
    title = models.CharField(max_length=200, null=True)
    identifier = models.CharField(max_length=200, null=True)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
    updated = models.BooleanField(default=False)
    enhanced_meta = GenericRelation(Metadata)
