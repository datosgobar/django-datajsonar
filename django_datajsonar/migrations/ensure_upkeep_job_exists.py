# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils import timezone


def create_upkeep_repeatable_job(apps, schema_editor):
    RepeatableJob = apps.get_model('scheduler', 'RepeatableJob')

    db_alias = schema_editor.connection.alias

    upkeep_jobs_count = RepeatableJob.objects.using(db_alias).\
        filter(callable='django_datajsonar.synchronizer.upkeep').count()

    if not upkeep_jobs_count:
        RepeatableJob.objects.using(db_alias).create(name='upkeep',
                                                     callable='django_datajsonar.synchronizer.upkeep',
                                                     queue='default',
                                                     scheduled_time=timezone.now(),
                                                     interval_unit='minutes',
                                                     interval=1,
                                                     repeat=None)


class Migration(migrations.Migration):

    dependencies = [
        ('django_datajsonar', '0020_auto_20190131_1213'),
        ('scheduler', '0003_remove_queue_choices')
    ]

    operations = [
        migrations.RunPython(create_upkeep_repeatable_job)
    ]
