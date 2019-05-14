#! coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from solo.models import SingletonModel


class Metadata(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "Additional metadata"

    key = models.CharField(max_length=64)
    value = models.TextField()

    # Generic foreign key magics
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class ProjectMetadata(SingletonModel):
    class Meta:
        verbose_name = "Project metadata"
    title = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=32, null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    issued = models.DateField(null=True, blank=True)
    modified_date = models.DateField(auto_now=True)


class Publisher(SingletonModel):
    name = models.CharField(max_length=128, null=True)
    mbox = models.CharField(max_length=128, null=True)
    modified_date = models.DateField(auto_now=True)
    project_metadata = models.OneToOneField(ProjectMetadata,
                                            on_delete=models.CASCADE,
                                            null=True)


class Language(models.Model):
    language = models.CharField(max_length=64)
    modified_date = models.DateField(auto_now=True)
    project_metadata = models.ForeignKey(ProjectMetadata,
                                         on_delete=models.CASCADE)


class Spatial(models.Model):
    spatial = models.CharField(max_length=64, null=True)
    modified_date = models.DateField(auto_now=True)
    project_metadata = models.ForeignKey(ProjectMetadata,
                                         on_delete=models.CASCADE)
