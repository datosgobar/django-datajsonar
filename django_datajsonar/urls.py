#! coding: utf-8
from django.conf.urls import url
from django_datajsonar.views import nodes_metadata_json, \
    nodes_english_metadata_csv, nodes_spanish_metadata_csv, \
    nodes_english_metadata_xlsx, nodes_spanish_metadata_xlsx, \
    distributions_spanish_metadata_csv

urlpatterns = [
    url(r'^nodes.json/$', nodes_metadata_json),
    url(r'^nodes.csv/$', nodes_english_metadata_csv),
    url(r'^nodos.csv/$', nodes_spanish_metadata_csv),
    url(r'^nodes.xlsx/$', nodes_english_metadata_xlsx),
    url(r'^nodos.xlsx/$', nodes_spanish_metadata_xlsx),
    url(r'^distribuciones.csv/$', distributions_spanish_metadata_csv),
]
