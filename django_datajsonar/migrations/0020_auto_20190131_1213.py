# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-31 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0019_auto_20190131_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='synchronizer',
            name='cron_string',
            field=models.CharField(max_length=64),
        ),
    ]