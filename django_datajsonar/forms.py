from django import forms


from scheduler.models import RepeatableJob


class ScheduleJobForm(forms.ModelForm):

    scheduled_time = forms.DateTimeField(widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
                                         input_formats=['%Y-%m-%dT%H:%M'])

    class Meta:
        model = RepeatableJob
        fields = ['name', 'callable', 'interval',
                  'interval_unit', 'scheduled_time', 'queue']
