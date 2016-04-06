from django.conf import settings
from django.conf.urls import include, url, patterns
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns(
    '',

    # admin urls
    url(r'^admin/', include(admin.site.urls)),

    # project-level urls
    url(r'^$', 'ids.views.homepage', name='homepage'),

    # auth
    url(r'^auth/', include('ids_auth.urls', namespace='ids_auth')),
    url(r'^login/$', 'ids_auth.views.agave_oauth', name='login'),
    url(r'^logout/$','django.contrib.auth.views.logout', { 'next_page': '/' }, name='logout'),
    # url(r'^', include('ids_auth.urls', namespace='ids_auth')),

    # projects
    url(r'^', include('ids_projects.urls', namespace='ids_projects')),
)
