#!coding=utf8

from datetime import timedelta

from django import forms
from django.conf import settings
from django.utils import timezone
from django.contrib.admin.widgets import AdminTimeWidget

from scheduler.models import RepeatableJob

from django_datajsonar.models import Synchronizer, Stage, AbstractTask
from django_datajsonar.utils import get_qualified_name


class ScheduleJobForm(forms.ModelForm):

    scheduled_time = forms.TimeField(widget=AdminTimeWidget(attrs={'type': 'time'}))

    class Meta:
        model = RepeatableJob
        fields = ['name', 'callable', 'interval',
                  'interval_unit', 'scheduled_time', 'queue']

    def clean_scheduled_time(self):
        # Convertir la hora a un datetime apropiado
        datetime = timezone.localtime()
        time = self.cleaned_data['scheduled_time']
        datetime = datetime.replace(hour=time.hour, minute=time.minute, second=0, microsecond=0)
        # Si la hora está en el pasado, lo programo para el día siguiente
        if datetime < timezone.now():
            datetime = datetime + timedelta(days=1)

        return datetime


class SynchroForm(forms.ModelForm):
    name = forms.CharField(max_length=50)
    stages_amount = forms.IntegerField(min_value=1)

    class Meta:
        model = Synchronizer
        exclude = ['start_stage', 'actual_stage', 'status']


class StageForm(forms.ModelForm):

    queue = forms.ChoiceField(choices=[(queue, queue) for queue in settings.RQ_QUEUES])
    task = forms.ChoiceField(choices=[(get_qualified_name(subclass), subclass.__name__)
                                      for subclass in AbstractTask.__subclasses__()] + [(None, "")],
                             required=False, )

    class Meta:
        model = Stage
        exclude = ('next_stage', 'status')


class StageFormset(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(StageFormset, self).__init__(*args, **kwargs)
        self.queryset = Stage.objects.none()
