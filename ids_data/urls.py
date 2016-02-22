from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'ids_data.views',
    url(r'^listing/(?P<system_id>[^/]+)/(?P<file_path>.+)?', 'files_list',
        name='files_list_json'),

    url(r'^$', 'index', name='index'),
    url(r'^(?P<parent_id>.+)/(?P<system_id>.+)/list/$', 'list', name='list'),
    url(r'^(.+)/create/$', 'create', name='create'),
    url(r'^delete/(.+)/$', 'delete', name='delete'),
    url(r'^edit/(.+)/$', 'edit', name='edit'),
    url(r'^(.+)/$', 'detail', name='detail'),

)
