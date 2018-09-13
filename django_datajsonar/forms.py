from django import forms
from django.contrib.admin.widgets import AdminTimeWidget

from scheduler.models import RepeatableJob


class ScheduleJobForm(forms.ModelForm):

    scheduled_time = forms.DateTimeField(widget=AdminTimeWidget(attrs={'type': 'time'}))

    class Meta:
        model = RepeatableJob
        fields = ['name', 'callable', 'interval',
                  'interval_unit', 'scheduled_time', 'queue']
