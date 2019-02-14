from __future__ import unicode_literals

from django.contrib import admin
from scheduler.admin import RepeatableJobAdmin
from scheduler.models import RepeatableJob

admin.site.unregister(RepeatableJob)


@admin.register(RepeatableJob)
class CustomRepeatableJobAdmin(RepeatableJobAdmin):
    actions = ['delete_and_unschedule']

    def delete_model(self, request, obj):
        obj.unschedule()
        return super(CustomRepeatableJobAdmin, self).delete_model(request, obj)

    def delete_and_unschedule(self, _, queryset):
        for job in queryset:
            job.unschedule()
        queryset.delete()

    delete_and_unschedule.short_description = 'Delete and unschedule job'

    def get_actions(self, request):
        actions = super(CustomRepeatableJobAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
