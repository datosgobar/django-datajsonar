#! coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Metadata(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "Additional metadata"

    key = models.CharField(max_length=64)
    value = models.TextField()

    # Generic foreign key magics
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
