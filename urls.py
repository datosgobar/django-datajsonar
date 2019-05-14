#! coding: utf-8
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'', include('django_datajsonar.urls', namespace="django_datajsonar")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
