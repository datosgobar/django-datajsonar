# django-datajsonar

## Instalación

Los requerimientos del proyecto se encuentran en la carpeta requirements. Se pueden instalar con
`pip install -r requirements/<tipo de instancia>`. `django-datajsonar` usa `django-rq` y `django-rq-scheduler`. Hay que
instalar las aplicaciones en los `settings`:
```
INSTALLED_APPS=[
...
'scheduler',
'django-rq',
'django_datajsonar'
...
]
```

Además usa una cola llamada `indexing`, para agregarla es necesario definir en los `settings`:
```
RQ_QUEUES = {
    'indexing': {
        'HOST': <REDIS_HOST>,
        'PORT': <REDIS_PORT>,
        'DB': <REDIS_DB>,
    },
}
``` 

Finalmente es necesario definir la lista de campos que deseamos ignorar de la red de nodos en los `settings``:

```python
CATALOG_BLACKLIST = []

DATASET_BLACKLIST = []

DISTRIBUTION_BLACKLIST = []

FIELD_BLACKLIST = []
```

Los campos definidos en esas listas no se cargan a la hora de generar los modelos.

## Uso

Ver [docs/uso.md](./docs/uso.md)

## Desarrollo

Se provee para pruebas manuales una aplicación ejemplo de Django con el `settings.py` configurado correctamente. Para levantarla:

- Levantar postgres y redis. Se provee un `docker-compose` ejemplo para ello, en el directorio raíz. `docker-compose up -d`
- Copiar los archivos `conf/settings/.env.example` a `conf/settings/.env`, `conf/settings/local_example.py` a `conf/settings/local.py`
- Exportar variable de configuración: `expot DJANGO_SETTINGS_MODULE=conf.settings.local`
- Correr migraciones: `./manage.py migrate`
- Levantar la aplicación: `./manage.py runserver`

## Tests

- `pip install -r requirements/testing.txt`
- `./scripts/tests.sh` 
