#! coding: utf-8
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from django_datajsonar.views import nodes_metadata_json

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^nodes.json/', nodes_metadata_json)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
