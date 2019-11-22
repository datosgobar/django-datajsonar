# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-31 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0019_auto_20191021_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='error_msg',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='error_msg',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='distribution',
            name='error_msg',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='field',
            name='error_msg',
            field=models.TextField(blank=True, default=''),
        ),
    ]