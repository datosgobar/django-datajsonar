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
        if datetime < timezone.localtime():
            datetime = datetime + timedelta(days=1)

        return datetime


class SynchroForm(forms.Form):
    name = forms.CharField(max_length=50)

    class Meta:
        model = Synchronizer
        exclude = ['start_stage', 'actual_stage', 'status']

    def create_synchronizer(self, start_stage):
        return Synchronizer.objects.create(name=self.cleaned_data['name'], start_stage=start_stage)


class StageForm(forms.Form):
    task = forms.ChoiceField(choices=[(x, x) for x in settings.DATAJSONAR_STAGES.keys()],
                             required=False, )

    class Meta:
        model = Stage
        exclude = ('next_stage', 'status', 'name', 'callable_str', 'queue')

    def get_stage(self, name):
        task = self.cleaned_data['task']

        data = settings.DATAJSONAR_STAGES[task]
        return Stage.objects.update_or_create(name=name, defaults=data)[0]


class StageFormset(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(StageFormset, self).__init__(*args, **kwargs)
        self.queryset = Stage.objects.none()
