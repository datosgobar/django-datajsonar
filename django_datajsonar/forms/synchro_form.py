from django import forms
from django.contrib.admin.widgets import AdminTimeWidget

from django_datajsonar import strings
from django_datajsonar.models import Synchronizer


class SynchroForm(forms.Form):
    name = forms.CharField(max_length=50)
    WEEK_DAYS = 'week days'
    DAILY = 'every day'
    FREQUENCY_CHOICES = (
        (DAILY, DAILY),
        (WEEK_DAYS, WEEK_DAYS),
    )

    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES)

    scheduled_time = forms.TimeField(
        widget=AdminTimeWidget(attrs={'type': 'time'}))

    MON = strings.MON
    TUE = strings.TUE
    WED = strings.WED
    THU = strings.THU
    FRI = strings.FRI
    SAT = strings.SAT
    SUN = strings.SUN

    WEEK_DAY_CHOICES = (
        (MON, 'Monday'),
        (TUE, 'Tuesday'),
        (WED, 'Wednesday'),
        (THU, 'Thursday'),
        (FRI, 'Friday'),
        (SAT, 'Saturday'),
        (SUN, 'Sunday'),
    )

    week_days = forms.MultipleChoiceField(choices=WEEK_DAY_CHOICES, required=False)

    def clean(self):
        cleaned_data = super(SynchroForm, self).clean()
        days = cleaned_data['week_days']
        frequency = cleaned_data['frequency']
        if frequency == self.WEEK_DAYS and not days:
            self.add_error('week_days', 'Days of week not selected')

        if Synchronizer.objects.filter(name=cleaned_data['name']):
            self.add_error('name', 'Synchronizer with this name already exists')
