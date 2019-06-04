#!coding=utf8
from collections import OrderedDict

NODES_ENGLISH_FIELDS = OrderedDict({
    "argentinagobar_id": "argentinagobar_id",
    "title": "jurisdiction_title",
    "id": "catalog_id",
    "label": "catalog_label",
    "url_json": "catalog_url_json",
    "url_xlsx": "catalog_url_xlsx",
    "url_datosgobar": "catalog_url_datosgobar",
    "url_homepage": "catalog_url_homepage",
})

NODES_SPANISH_FIELDS = OrderedDict({
    "argentinagobar_id": "argentinagobar_id",
    "title": "jurisdiccion_nombre",
    "id": "catalogo_id",
    "label": "catalogo_nombre",
    "url_json": "catalogo_url_json",
    "url_xlsx": "catalogo_url_xlsx",
    "url_datosgobar": "catalogo_url_datosgobar",
    "url_homepage": "catalogo_url_portal",
})

DISTRIBUTIONS_SPANISH_FIELDS = OrderedDict({
    'identifier': 'distribucion_id',
    'title': 'distribucion_titulo',
    'download_url': 'distribucion_url_descarga',
    'dataset__identifier': 'dataset_id',
    'dataset__title': 'dataset_titulo',
    'dataset__catalog__title': 'catalogo_titulo',
    'dataset__catalog__identifier': 'catalogo_id',
})
