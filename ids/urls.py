from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns('',

    # TODO admin

    # auth
    url(r'^auth/', include('ids.apps.auth.urls', namespace='ids_auth')),
    url(r'^login/$', 'ids.apps.auth.views.login_options', name='login'),
    url(r'^logout/$','django.contrib.auth.views.logout', { 'next_page': '/' }, name='logout'),

) #TODO + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
