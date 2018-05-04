# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-03 21:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='field',
            name='error',
        ),
        migrations.AddField(
            model_name='dataset',
            name='title',
            field=models.CharField(default='No Title', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='field',
            name='identifier',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='field',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
