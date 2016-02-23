from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'ids_systems.views',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<parent_id>.+)/index/$', 'index', name='index'),
    url(r'^(.+)/create/$', 'create', name='create'),
    url(r'^delete/(.+)/$', 'delete', name='delete'),
    url(r'^edit/(.+)/$', 'edit', name='edit'),
    url(r'^(.+)/$', 'detail', name='detail'),
    url(r'^list.json$', 'systems_list', name='systems_list_json')
)
