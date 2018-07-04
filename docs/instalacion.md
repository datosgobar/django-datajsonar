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
