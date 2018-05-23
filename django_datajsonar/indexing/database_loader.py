#! coding: utf-8
import hashlib
import json

from tempfile import NamedTemporaryFile

import requests
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from pydatajson import DataJson
from pydatajson.time_series import distribution_has_time_index

from django_datajsonar.models import ReadDataJsonTask
from django_datajsonar.models import Dataset, Catalog, Distribution, Field
from . import constants
from .utils import log_exception, update_model


class DatabaseLoader(object):
    """Carga la base de datos. No hace validaciones"""

    def __init__(self, task, read_local=False, default_whitelist=False):
        self.task = task
        self.catalog_model = None
        self.catalog_id = None
        self.stats = {}
        self.read_local = read_local
        self.default_whitelist = default_whitelist

    def run(self, catalog, catalog_id):
        """Guarda la metadata del catalogo pasado por parametro

        Args:
            catalog (DataJson)
            catalog_id (str): Identificador único del catalogo a guardar
        Returns:
            Catalog: el modelo de catalogo creado o actualizado
        """
        self.catalog_id = catalog_id
        self.catalog_model = self._catalog_model(catalog, catalog_id)
        return self.catalog_model

    def _catalog_model(self, catalog, catalog_id):
        """Crea o actualiza el catalog model con el título pedido a partir
        de el diccionario de metadatos de un catálogo
        """
        trimmed_catalog = self._trim_dict_fields(
            catalog, settings.CATALOG_BLACKLIST, constants.DATASET)

        catalog_model, created = Catalog.objects.update_or_create(
            identifier=catalog_id,
            defaults={'title': trimmed_catalog.get('title', 'No Title')}
        )

        only_time_series = getattr(settings, 'DATAJSON_AR_TIME_SERIES_ONLY', False)
        datasets = catalog.get_datasets(only_time_series=only_time_series)
        updated_datasets = False
        for dataset in datasets:
            try:
                dataset_model = self._dataset_model(dataset, catalog_model)
                updated_datasets = updated_datasets or dataset_model.updated
            except Exception as e:
                msg = u"Excepción en dataset {}: {}"\
                    .format(dataset.get('identifier'), e)
                model_fields = {'identifier': dataset.get('identifier'),
                                'catalog': catalog_model}
                log_exception(self.task, msg, Dataset, model_fields)
                continue

        if not datasets and only_time_series:
            msg = u"No fueron encontrados series de tiempo en el catálogo {}".format(catalog_id)
            ReadDataJsonTask.info(self.task, msg)

        update_model(created, trimmed_catalog, catalog_model, updated_children=updated_datasets)
        return catalog_model

    def _dataset_model(self, dataset, catalog_model):
        """Crea o actualiza el modelo del dataset a partir de un
        diccionario que lo representa
        """
        trimmed_dataset = self._trim_dict_fields(
            dataset, settings.DATASET_BLACKLIST, constants.DISTRIBUTION)
        identifier = trimmed_dataset[constants.IDENTIFIER]
        dataset_model, created = Dataset.objects.update_or_create(
            catalog=catalog_model,
            identifier=identifier,
            defaults={'title': trimmed_dataset.get('title', 'No Title')}
        )
        updated_distributions = False
        distributions = dataset.get('distribution', [])
        if getattr(settings, 'DATAJSON_AR_TIME_SERIES_ONLY', False):
            distributions = [dist for dist in distributions if distribution_has_time_index(dist)]
        for distribution in distributions:
            try:
                distribution_model = self._distribution_model(distribution, dataset_model)
                updated_distributions = updated_distributions or distribution_model.updated
            except Exception as e:
                msg = u"Excepción en distribución {}: {}"\
                    .format(distribution.get('identifier'), e)
                model_fields = {'identifier': distribution.get('identifier'),
                                'dataset': dataset_model}
                log_exception(self.task, msg, Distribution, model_fields)
                continue

        if self.default_whitelist:
            dataset_model.indexable = True

        update_model(created, trimmed_dataset, dataset_model, updated_children=updated_distributions)
        return dataset_model

    def _distribution_model(self, distribution, dataset_model):
        """Crea o actualiza el modelo de la distribución a partir de
        un diccionario que lo representa
        """
        trimmed_distribution = self._trim_dict_fields(
            distribution, settings.DISTRIBUTION_BLACKLIST, constants.FIELD)
        url = trimmed_distribution.get(constants.DOWNLOAD_URL)
        distribution_model, created = Distribution.objects.update_or_create(
            dataset=dataset_model,
            identifier=trimmed_distribution[constants.IDENTIFIER],
            defaults={
                'title': trimmed_distribution.get(constants.TITLE, 'No Title'),
                'download_url': url
            }
        )

        updated_fields = False
        for field in distribution.get('field', []):
            try:
                field_model = self._field_model(field, distribution_model)
                updated_fields = updated_fields or field_model.updated
            except Exception as e:
                msg = u"Excepción en field {}: {}"\
                    .format(field.get('title'), e)
                model_fields = {'identifier': field.get('identifier'),
                                'distribution': distribution_model}
                log_exception(self.task, msg, Field, model_fields)
                continue

        data_change = False
        if (dataset_model.indexable or self.default_whitelist) and url:
            data_change = self._read_file(url, distribution_model)

        # En caso de que no descargue el archivo.
        if not url:
            distribution_model.error = True

        update_model(created, trimmed_distribution, distribution_model,
                     updated_children=updated_fields, data_change=data_change)
        return distribution_model

    def _field_model(self, field, distribution_model):
        trimmed_field = self._trim_dict_fields(
            field, settings.FIELD_BLACKLIST
        )
        field_meta = json.dumps(trimmed_field)
        field_model, created = Field.objects.get_or_create(
            distribution=distribution_model,
            title=field.get('title'),
            identifier=field.get('id'),
            defaults={'metadata': field_meta}
        )
        update_model(created, trimmed_field, field_model)
        return field_model

    def _read_file(self, file_url, distribution_model):
        """Descarga y lee el archivo de la distribución. Por razones
        de performance, NO hace un save() a la base de datos.
        Marca el modelo de distribución como 'indexable' si el archivo tiene datos
        distintos a los actuales. El chequeo de cambios se hace hasheando el archivo entero
        Args:
            file_url (str)
            distribution_model (Distribution)
        """
        if self.read_local:  # Usado en debug y testing
            with open(file_url) as f:
                data_hash = hashlib.sha512(f.read().encode('utf-8')).hexdigest()

            distribution_model.data_file = File(open(file_url))

        else:
            request = requests.get(file_url, stream=True)
            request.raise_for_status()  # Excepción si es inválido

            lf = NamedTemporaryFile()

            lf.write(request.content)

            if distribution_model.data_file:
                distribution_model.data_file.delete()

            distribution_model.data_file = File(lf)
            data_hash = hashlib.sha512(request.content).hexdigest()

        if distribution_model.data_hash != data_hash:
            distribution_model.data_hash = data_hash
            distribution_model.last_updated = timezone.now()

        return distribution_model.data_hash != data_hash

    @staticmethod
    def _remove_blacklisted_fields(metadata, blacklist):
        """Borra los campos listados en 'blacklist' de el diccionario
        'metadata'
        """
        for field in blacklist:
            metadata.pop(field, None)
        return metadata

    def _trim_dict_fields(self, full_dict, blacklist, children=None):
        trimmed_dict = full_dict.copy()
        if children:
            trimmed_dict.pop(children, None)
        trimmed_dict = self._remove_blacklisted_fields(
            trimmed_dict, blacklist)
        return trimmed_dict
