#! coding: utf-8
from django.conf.urls import url
from django_datajsonar.views import nodes_metadata_json

urlpatterns = [
    url(r'^nodes.json/', nodes_metadata_json)
]
