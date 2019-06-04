# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-17 17:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0009_dataset_landing_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readdatajsontask',
            name='node',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_datajsonar.Node'),
        ),
    ]