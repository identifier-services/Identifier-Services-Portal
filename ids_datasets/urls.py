from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'ids_datasets.views',
    url(r'^$', 'index', name='index'),
    url(r'^(.+)/index/$', 'index', name='index'),
    url(r'^(.+)/create/$', 'create', name='create'),
    url(r'^delete/(.+)/$', 'delete', name='delete'),
    url(r'^edit/(.+)/$', 'edit', name='edit'),
    url(r'^(.+)/$', 'detail', name='detail'),
)
