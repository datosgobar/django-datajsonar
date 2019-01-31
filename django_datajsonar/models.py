#! coding: utf-8
from __future__ import unicode_literals

from datetime import datetime
from importlib import import_module

from croniter import croniter, CroniterBadCronError
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django_datajsonar.utils import pending_or_running_jobs, import_string


class Metadata(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "Metadatos enriquecidos"

    key = models.CharField(max_length=64)
    value = models.TextField()

    # Generic foreign key magics
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class Catalog(models.Model):
    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, unique=True)
    metadata = models.TextField()
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata, null=True)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.identifier)

    def __str__(self):
        return self.__unicode__()


class Dataset(models.Model):

    REVIEWED = "REVIEWED"
    ON_REVISION = "ON_REVISION"
    NOT_REVIEWED = "NOT_REVIEWED"

    REVIEWED_STATUS = (
        (REVIEWED, "Revisado"),
        (ON_REVISION, "En revisión"),
        (NOT_REVIEWED, "No revisado"),
    )

    title = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
    metadata = models.TextField()
    catalog = models.ForeignKey(to=Catalog, on_delete=models.CASCADE)
    indexable = models.BooleanField(default=False)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    reviewed = models.CharField(max_length=20, choices=REVIEWED_STATUS, default=NOT_REVIEWED)
    last_reviewed = models.DateField(null=True, blank=True, default=None)

    themes = models.TextField(blank=True, null=True)

    enhanced_meta = GenericRelation(Metadata)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


def filepath(instance, _):
    """Método para asignar el nombre al archivo fuente del FileField
    del modelo Distribution
    """
    return u'distribution_raw/{}/{}.csv'.format(instance.dataset.catalog.identifier, instance.identifier)


def get_distribution_storage():
    """Importa dinámicamente el módulo configurado en el setting
    DATAJSON_AR_DISTRIBUTION_STORAGE, y devuelve una instancia
    del objeto determinado. De no existir, devuelve el storage default
    """
    data_file_storage_path = getattr(settings, 'DATAJSON_AR_DISTRIBUTION_STORAGE', None)
    if data_file_storage_path is None:
        return default_storage

    split = data_file_storage_path.split('.')
    module = import_module('.'.join(split[:-1]))

    storage = getattr(module, split[-1], None)
    if storage is None:
        raise ImproperlyConfigured

    return storage()


class Distribution(models.Model):
    identifier = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    metadata = models.TextField()
    dataset = models.ForeignKey(to=Dataset, on_delete=models.CASCADE)
    download_url = models.URLField(max_length=1024, null=True)
    data_hash = models.CharField(max_length=128, default='')
    last_updated = models.DateTimeField(blank=True, null=True)

    data_file = models.FileField(
        storage=get_distribution_storage(),
        max_length=2000,
        upload_to=filepath,
        blank=True
    )
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' % (self.identifier, self.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class Field(models.Model):
    title = models.CharField(max_length=200, null=True)
    identifier = models.CharField(max_length=200, null=True)
    metadata = models.TextField()
    distribution = models.ForeignKey(to=Distribution, on_delete=models.CASCADE)
    present = models.BooleanField(default=True)
    updated = models.BooleanField(default=True)
    error = models.BooleanField(default=False)

    enhanced_meta = GenericRelation(Metadata)
    new = models.BooleanField(default=False)

    error_msg = models.TextField(default='')

    def __unicode__(self):
        return u'%s (%s)' %\
               (self.title or 'Field sin title',
                self.distribution.dataset.catalog.identifier)

    def __str__(self):
        return self.__unicode__()


class BaseRegisterFile(models.Model):
    """Base de los archivos de registro de datasets y de nodos.
    Contiene atributos de estado del archivo y fechas de creado / modificado
    """
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

    STATE_CHOICES = (
        (UPLOADED, "Cargado"),
        (PROCESSING, "Procesando"),
        (PROCESSED, "Procesado"),
        (FAILED, "Error"),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    indexing_file = models.FileField(upload_to='register_files/')
    uploader = models.ForeignKey(User)
    state = models.CharField(max_length=20, choices=STATE_CHOICES)
    logs = models.TextField(default=u'-')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.state = self.UPLOADED

        super(BaseRegisterFile, self).save(force_insert, force_update, using, update_fields)


class NodeRegisterFile(BaseRegisterFile):
    def __unicode__(self):
        return "Node register file: {}".format(self.created)

    def __str__(self):
        return self.__unicode__()


class DatasetIndexingFile(BaseRegisterFile):
    def __unicode__(self):
        return "Indexing file: {}".format(self.created)

    def __str__(self):
        return self.__unicode__()


class Jurisdiction(models.Model):
    jurisdiction_title = models.CharField(max_length=100, unique=True)
    jurisdiction_id = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return "%s" % self.jurisdiction_title

    def __str__(self):
        return self.__unicode__()


class Node(models.Model):
    CKAN = "ckan"
    XLSX = "xlsx"
    JSON = "json"
    FORMATS = (
        (CKAN, "Portal CKAN"),
        (XLSX, "Catálogo XLSX"),
        (JSON, "Catálogo JSON"),
    )

    catalog_id = models.CharField(max_length=100, unique=True)
    catalog_url = models.URLField()
    indexable = models.BooleanField()
    catalog = models.TextField(default='{}')
    admins = models.ManyToManyField(User, blank=True)
    catalog_format = models.CharField(max_length=20, choices=FORMATS,
                                      null=True, blank=True)
    register_date = models.DateField(default=timezone.now)
    release_date = models.DateField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.release_date is None and self.indexable is True:
            self.release_date = timezone.now().date()
        super(Node, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.catalog_id

    def __str__(self):
        return self.__unicode__()


class NodeMetadata(models.Model):
    class Meta:
        verbose_name = verbose_name_plural = "Node Metadata"

    CENTRAL = "central"
    NO_CENTRAL = "no-central"
    CATEGORIES = (
        (CENTRAL, "Catálogo central"),
        (NO_CENTRAL, "Catálogo no central")
    )

    ANDINO = "andino"
    EXCEL = "excel"
    OTHER = "other"
    CKAN = "ckan"
    TYPES = (
        (ANDINO, "Andino"),
        (EXCEL, "Excel"),
        (CKAN, "CKAN"),
        (OTHER, "Otros")
    )
    argentinagobar_id = models.CharField(max_length=50, null=True, blank=True)
    catalog_label = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES,
                                null=True, blank=True)
    types = models.CharField(max_length=20, choices=TYPES,
                             null=True, blank=True)
    jurisdiction = models.ForeignKey(to=Jurisdiction, null=True,
                                     blank=True, on_delete=models.SET_NULL)
    json_url = models.URLField(null=True, blank=True)
    xlsx_url = models.URLField(null=True, blank=True)
    datosgobar_url = models.URLField(null=True, blank=True)
    homepage_url = models.URLField(null=True, blank=True)
    node = models.OneToOneField(Node, on_delete=models.CASCADE,
                                primary_key=True)


class AbstractTask(models.Model):

    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"

    STATUS_CHOICES = (
        (RUNNING, "Procesando catálogos"),
        (FINISHED, "Finalizada"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    logs = models.TextField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pk:  # first time only
            self.status = self.RUNNING

        super(AbstractTask, self).save(force_insert, force_update,
                                       using, update_fields)

    def __unicode__(self):
        return "Task at %s" % self._format_date(self.created)

    def __str__(self):
        return self.__unicode__()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @classmethod
    def info(cls, task, msg):
        with transaction.atomic():
            task = cls.objects.select_for_update().get(id=task.id)
            task.logs += msg + '\n'
            task.save()

    class Meta:
        abstract = True


class ReadDataJsonTask(AbstractTask):
    COMPLETE_RUN = True
    METADATA_ONLY = False
    INDEXING_CHOICES = ((COMPLETE_RUN, 'Corrida completa'), (METADATA_ONLY, 'Corrida solo de metadatos'),)
    default_mode = getattr(settings, 'DATAJSON_AR_DOWNLOAD_RESOURCES', True)
    indexing_mode = models.BooleanField(choices=INDEXING_CHOICES, default=default_mode)


class Stage(models.Model):

    ACTIVE = True
    INACTIVE = False

    STATUS_CHOICES = (
        (ACTIVE, "Tarea activa"),
        (INACTIVE, "Tarea inactiva"),
    )

    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False, choices=STATUS_CHOICES)
    callable_str = models.CharField(max_length=100)
    queue = models.CharField(max_length=50)
    next_stage = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    task = models.CharField(max_length=200, blank=True)

    def get_running_task(self):
        if self.task:
            task_model = import_string(self.task)
        else:
            return None
        try:
            return task_model.objects.filter(status=task_model.RUNNING).latest('created')
        except task_model.DoesNotExist:
            return None

    def open_stage(self):
        job = import_string(self.callable_str)
        job.delay()
        self.status = Stage.ACTIVE
        self.save()

    def close_stage(self):
        task = self.get_running_task()
        if task:
            # Cierra la tarea si quedó abierta
            task.status = task.FINISHED
            task.save()
        self.status = self.INACTIVE
        self.save()

    def check_completion(self):
        return not pending_or_running_jobs(self.queue)

    def clean(self):
        errors = {}
        try:
            method = import_string(self.callable_str)
            if not callable(method):
                msg = 'callable_str must be callable: {}'.format(self.callable_str)
                errors.update({'callable_str': ValidationError(msg)})

            if not hasattr(method, 'delay'):
                msg = 'method referenced is not an rq job (has no "delay" attribute: {}'.format(self.callable_str)
                errors.update({'callable_str': msg})

        except (ImportError, ValueError):
            msg = 'Unable to import callable_str: {}'.format(self.callable_str)
            errors.update({'callable_str': ValidationError(msg)})

        if self.queue not in settings.RQ_QUEUES:
            msg = 'Queue is not defined in settings: {}'.format(self.queue)
            errors.update({'queue': ValidationError(msg)})

        if self.task:
            try:
                task_model = import_string(self.task)
                if not issubclass(task_model, AbstractTask):
                    msg = 'task must be an AbstractTask subclass: {}'.format(self.task)
                    errors.update({'task': ValidationError(msg)})
            except (ImportError, TypeError, ValueError):
                errors.update({'task': ValidationError('If present, task must be importable')})

        if self.next_stage and self.pk and self.next_stage.pk == self.pk:
            msg = 'next_stage must point to a different_stage: {}'.format(self)
            errors.update({'next_stage': ValidationError(msg)})

        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(Stage, self).save(force_insert=False, force_update=False, using=None,
                                update_fields=None)

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.queue)

    def __str__(self):
        return self.__unicode__()


class Synchronizer(models.Model):

    RUNNING = True
    STAND_BY = False

    STATUS_CHOICES = (
        (RUNNING, "Corriendo procesos"),
        (STAND_BY, "En espera"),
    )

    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=False, choices=STATUS_CHOICES)

    start_stage = models.ForeignKey(to=Stage, related_name='synchronizer', on_delete=models.PROTECT)
    actual_stage = models.ForeignKey(to=Stage, related_name='running_synchronizer', null=True, blank=True,
                                     on_delete=models.PROTECT)

    cron_string = models.CharField(max_length=64)
    last_time_ran = models.DateTimeField(auto_now_add=True)

    def clean(self):
        try:
            self.next_start_date()
        except CroniterBadCronError:
            raise ValidationError({'cron_string': "Invalid cron string: {}".format(self.cron_string)})

    def begin_stage(self, stage=None):
        if self.status == self.RUNNING and stage is None:
            raise Exception('El synchronizer ya está corriendo, pero no se pasó la siguiente etapa.')
        stage = stage or self.start_stage
        self.status = self.RUNNING
        self.actual_stage = stage
        self.last_time_ran = timezone.now()
        self.save()
        stage.open_stage()

    def check_completion(self):
        if self.status != self.RUNNING:
            raise Exception('El synchronizer no está corriendo')
        return self.actual_stage.check_completion()

    def next_stage(self):
        if self.status != self.RUNNING:
            raise Exception('El synchronizer no está corriendo')
        self.actual_stage.close_stage()
        if self.actual_stage.next_stage is None:
            self.status = self.STAND_BY
            self.actual_stage = None
            self.save()
        else:
            self.begin_stage(self.actual_stage.next_stage)

    def next_start_date(self):
        localtime = self.last_time_ran.astimezone(timezone.get_current_timezone())
        return croniter(self.cron_string, start_time=localtime).get_next(datetime)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()
