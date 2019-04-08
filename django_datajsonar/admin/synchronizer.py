#! coding: utf-8
from __future__ import unicode_literals

import json

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django_datajsonar.forms.manual_synchronizer_form import ManualSynchronizerRunForm
from django_datajsonar.forms.stage_form import StageForm
from django_datajsonar.forms.synchro_form import SynchroForm
from django_datajsonar.models import Synchronizer, Node
from django_datajsonar.synchronizer import create_or_update_synchro
from django_datajsonar.utils.utils import generate_stages


@admin.register(Synchronizer)
class SynchronizerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'frequency', 'scheduled_time', 'weekdays')
    actions = ('duplicate',)
    StageFormset = formset_factory(StageForm, extra=0)

    def add_view(self, request, form_url='', extra_context=None):
        return self._synchro_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super(SynchronizerAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        extra_urls = [url(r'^start_synchro/(?P<synchro_id>[0-9])$',
                          self.admin_site.admin_view(self.start_synchro),
                          name='%s_%s_start_synchro' % info), ]
        return extra_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        synchro = Synchronizer.objects.get(id=object_id)
        return self._synchro_view(request, synchro, extra_context=extra_context)

    def _synchro_view(self, request, synchro=None, extra_context=None):
        extra_context = extra_context or {}
        if request.method == 'POST':
            return self.post_synchro_edit(request, synchro.id if synchro else None)

        if synchro is not None:
            synchro_form = SynchroForm({
                'name': synchro.name,
                'frequency': synchro.frequency,
                'scheduled_time': synchro.scheduled_time,
                'week_days': synchro.get_days_of_week()
            })
        else:
            synchro_form = SynchroForm(extra_context)

        stages_formset = extra_context.get('stages_formset')
        context = self.add_synchro_context(request, synchro_form, synchro, stages_formset)

        return render(request, 'synchronizer.html', context)

    def add_synchro_context(self, request, synchro_form, synchro=None, stages_formset=None):
        context = {
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
            'synchro_form': self.admin_synchro_form(request, synchro_form),
            'stages_form': stages_formset or self.get_stages_formset(synchro),
            'object': synchro,
        }
        return context

    def get_stages_formset(self, model=None):
        stages_data = []
        next_stage = model.start_stage if model else None
        while next_stage is not None:
            stages_data.append({
                'task': self.get_stage_choice(next_stage.name)
            })
            next_stage = next_stage.next_stage

        if not stages_data:
            stages_data.append({})

        return self.StageFormset(initial=stages_data)

    def admin_synchro_form(self, request, synchro_form):
        return helpers.AdminForm(synchro_form,
                                 list([(None, {'fields': synchro_form.base_fields})]),
                                 self.get_prepopulated_fields(request))

    def post_synchro_edit(self, request, object_id=None):
        synchro = Synchronizer.objects.get(id=object_id) if object_id else None
        synchro_form = SynchroForm(request.POST)
        stages_formset = self.StageFormset(request.POST)

        if not stages_formset.is_valid() or not synchro_form.is_valid():
            synchro = Synchronizer.objects.get(id=object_id) if object_id else None
            return render(request, 'synchronizer.html', self.add_synchro_context(request, synchro_form, synchro))

        synchro_name = synchro_form.cleaned_data['name']
        stages = generate_stages(stages_formset.forms, synchro_name)
        if not stages:
            messages.error(request, "No hay stages definidos")
            return render(request, 'synchronizer.html', self.add_synchro_context(request, synchro_form, synchro))

        data = {
            'name': synchro_name,
            'frequency': synchro_form.cleaned_data['frequency'],
            'scheduled_time': synchro_form.cleaned_data['scheduled_time'],
            'week_days': json.dumps(synchro_form.cleaned_data['week_days']),
        }
        create_or_update_synchro(object_id, stages, data)

        return redirect('admin:django_datajsonar_synchronizer_changelist')

    def get_stage_choice(self, stage_name):
        for name in settings.DATAJSONAR_STAGES.keys():
            if name in stage_name:
                return name
        raise ValueError("Invalid stage name: {}".format(stage_name))

    def weekdays(self, obj):
        if obj.frequency == Synchronizer.WEEK_DAYS:
            return ', '.join(obj.get_days_of_week())
        return '-'
    weekdays.short_description = 'Week days'

    def duplicate(self, _, queryset):
        for synchronizer in queryset:
            # Duplica el synchronizer
            synchronizer.pk = None
            synchronizer.name = "Copia de {}".format(synchronizer.name)
            synchronizer.save()
    duplicate.short_description = "Duplicar synchronizer"

    def start_synchro(self, request, synchro_id):
        synchro = Synchronizer.objects.get(id=synchro_id)
        if request.method == 'POST':
            try:
                synchro.node = Node.objects.get(id=request.POST.get('node'))
                synchro.begin_stage()
                messages.success(request, "Corriendo tarea!")
            except Exception:
                messages.error(request, "El synchronizer seleccionado ya está corriendo")
            return redirect('admin:django_datajsonar_synchronizer_changelist')

        context = {
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
            'form': ManualSynchronizerRunForm(),
            'object': synchro,
        }
        return render(request, 'synchronizer_manual_run.html', context=context)
