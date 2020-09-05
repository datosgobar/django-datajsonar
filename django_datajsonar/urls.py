#! coding: utf-8
from django.conf.urls import url

from django_datajsonar.views import nodes_metadata_json, \
    nodes_english_metadata_csv, nodes_spanish_metadata_csv, \
    nodes_english_metadata_xlsx, nodes_spanish_metadata_xlsx, \
    distributions_spanish_metadata_csv, distributions_spanish_metadata_xlsx, json_catalog, \
    xlsx_catalog, validator_success, ValidatorView

urlpatterns = [
    url(r'^nodes.json/$', nodes_metadata_json, name='nodes_json'),
    url(r'^nodes.csv/$', nodes_english_metadata_csv, name='nodes_csv'),
    url(r'^nodos.csv/$', nodes_spanish_metadata_csv, name='nodos_csv'),
    url(r'^nodes.xlsx/$', nodes_english_metadata_xlsx, name='nodes_xlsx'),
    url(r'^nodos.xlsx/$', nodes_spanish_metadata_xlsx, name='nodos_json'),
    url(r'^distribuciones.csv/$', distributions_spanish_metadata_csv,
        name='distribuciones_csv'),
    url(r'^distribuciones.xlsx/$', distributions_spanish_metadata_xlsx,
        name='distribuciones_xlsx'),
    url(r'^catalog/(?P<catalog_id>[\w]+)/data.json', json_catalog, name="json_catalog"),
    url(r'^catalog/(?P<catalog_id>[\w]+)/catalog.xlsx', xlsx_catalog, name="xlsx_catalog"),
    url(r'^validator/$', ValidatorView.as_view(), name="validator"),
    url(r'validator_success/$', validator_success, name="validator_success")

]
