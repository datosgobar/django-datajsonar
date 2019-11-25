import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views import View

from django_datajsonar.models import Synchronizer, Stage


class RestoreDefaultSynchronizerView(View):
    model = Synchronizer

    def get(self, request):
        if not hasattr(settings, 'SYNCHRO_DEFAULT_CONF'):
            messages.error(request, "No hay definida una configuración default para los synchronizers")
            return redirect('admin:django_datajsonar_synchronizer_changelist')

        context = {
            'title': 'Restore default synchronizers',
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'restore_default_confirmation.html', context=context)

    def post(self, request):
        Synchronizer.objects.all().delete()
        Stage.objects.all().delete()

        synchro_list = settings.SYNCHRO_DEFAULT_CONF
        stage_dict = settings.DATAJSONAR_STAGES
        for synchro in synchro_list:
            top_stage = None
            for stage in synchro['stages'][::-1]:
                stage_fields = {
                    'name': synchro['title'] + ': ' + stage,
                    'callable_str': stage_dict[stage]['callable_str'],
                    'queue': stage_dict[stage]['queue'],
                    'next_stage': top_stage,
                }
                top_stage = Stage.objects.create(**stage_fields)

            scheduled_time = datetime.strptime(synchro['scheduled_time'], '%H:%M')
            synchro_fields = {
                'name': synchro['title'],
                'start_stage': top_stage,
                'actual_stage': None,
                'scheduled_time': scheduled_time,
            }
            if 'week_days' in synchro:
                synchro_fields.update({
                    'frequency': Synchronizer.WEEK_DAYS,
                    'week_days': json.dumps(synchro['week_days'])
                })
            Synchronizer.objects.create(**synchro_fields)
        messages.success(request, "Restaurados synchronizers defaults!")
        return redirect('admin:django_datajsonar_synchronizer_changelist')
