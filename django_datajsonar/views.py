#!coding=utf8

from django.shortcuts import render, redirect

from .models import Dataset
from .utils import download_config_csv
from .forms import ScheduleJobForm


def config_csv(_):
    datasets = Dataset.objects.filter(indexable=True)
    return download_config_csv(datasets)


def schedule_task(request, callable_str=None):
    form = ScheduleJobForm({'callable': callable_str, 'queue': 'indexing'})
    display_errors = False

    if request.method == 'POST':
        form = ScheduleJobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin:scheduler_repeatablejob_changelist')
        else:
            display_errors = True

    if callable_str is not None:
        form.fields['callable'].widget.attrs['readonly'] = True
    form.fields['queue'].widget.attrs['readonly'] = True
    return render(request, 'scheduler.html', {'form': form, 'display_errors': display_errors})
