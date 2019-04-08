from django import forms

from django_datajsonar.models import Node


class ManualSynchronizerRunForm(forms.Form):
    node = forms.ModelChoiceField(queryset=Node.objects.filter(indexable=True))
