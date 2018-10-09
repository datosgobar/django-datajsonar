#!coding=utf8

from datetime import timedelta

from django import forms
from django.utils import timezone
from django.contrib.admin.widgets import AdminTimeWidget

from scheduler.models import RepeatableJob


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
