from django import forms
from django.conf import settings

from django_datajsonar.models import Stage


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
