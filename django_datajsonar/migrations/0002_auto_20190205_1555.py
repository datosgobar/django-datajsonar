# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-05 18:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0001_auto_20190201_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='synchronizer',
            name='week_days',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='synchronizer',
            name='frequency',
            field=models.CharField(choices=[('every day', 'Every day'), ('week days', 'Week days')], default='every day', max_length=16),
        ),
    ]
