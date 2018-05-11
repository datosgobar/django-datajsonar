#!/usr/bin/env bash


python manage.py test --stop --with-coverage --cover-branches  --cover-inclusive --cover-package=django_datajsonar --settings=conf.settings.testing --exclude=settings --exclude=migrations
