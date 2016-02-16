from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'ids_data.views',
    url(r'^system/$', 'system', name='system'),

    url(r'^$', 'index', name='index'),
    url(r'^(.+)/list/$', 'index', name='index'),
    url(r'^(.+)/create/$', 'create', name='create'),
    url(r'^delete/(.+)/$', 'delete', name='delete'),
    url(r'^edit/(.+)/$', 'edit', name='edit'),
    url(r'^(.+)/$', 'detail', name='detail'),
)
