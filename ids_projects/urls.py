from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'ids_projects.views',
    url(r'^$', 'index', name='index'),
    url(r'^create/$', 'create', name='create'),
    url(r'^(.+)/$', 'detail', name='detail'),
)
