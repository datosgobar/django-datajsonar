# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-01 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0002_auto_20190205_1555'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasetindexingfile',
            options={'verbose_name': 'Dataset federation file'},
        ),
        migrations.AlterModelOptions(
            name='readdatajsontask',
            options={'verbose_name': 'Node read task'},
        ),
        migrations.AlterField(
            model_name='synchronizer',
            name='scheduled_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
    ]
