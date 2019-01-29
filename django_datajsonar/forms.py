#!coding=utf8

from datetime import timedelta

from django import forms
from django.conf import settings
from django.utils import timezone
from django.contrib.admin.widgets import AdminTimeWidget, AdminDateWidget

from scheduler.models import RepeatableJob

from django_datajsonar.models import Synchronizer, Stage, AbstractTask
from django_datajsonar.utils import get_qualified_name


class ScheduleJobForm(forms.ModelForm):

    class Meta:
        model = RepeatableJob
        fields = ['name', 'interval_unit', 'interval',
                  'scheduled_time', 'starting_date',
                  'callable', 'queue']

    scheduled_time = forms.TimeField(
        widget=AdminTimeWidget(attrs={'type': 'time'}))
    starting_date = forms.DateField(
        widget=AdminDateWidget(attrs={'type': 'date'}),
        required=False
    )

    def clean_scheduled_time(self):
        # Convertir la hora a un datetime apropiado
        clean_datetime = timezone.localtime()
        scheduled_time = self.cleaned_data['scheduled_time']
        clean_datetime = clean_datetime.replace(hour=scheduled_time.hour,
                                                minute=scheduled_time.minute,
                                                second=0, microsecond=0)
        # Si la hora está en el pasado, lo programo para el día siguiente
        if clean_datetime < timezone.localtime():
            clean_datetime = clean_datetime + timedelta(days=1)
        return clean_datetime

    def clean(self):
        cleaned_data = super(ScheduleJobForm, self).clean()
        interval_unit = cleaned_data.get('interval_unit')
        if interval_unit == 'weeks':
            starting_date = cleaned_data.get('starting_date')
            if not starting_date:
                self.add_error('starting_date', 'This is a required field')
                return cleaned_data
            scheduled_time = self.cleaned_data.get('scheduled_time')
            scheduled_time = scheduled_time.replace(year=starting_date.year,
                                                    month=starting_date.month,
                                                    day=starting_date.day)
            if scheduled_time < timezone.localtime():
                self.add_error('starting_date', 'Date cannot be in the past')
            cleaned_data['scheduled_time'] = scheduled_time
        return cleaned_data


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
