from django.conf.urls import include, url, patterns
from django.contrib import admin

urlpatterns = patterns(
    '',

    # admin urls
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/impersonate/', include('hijack.urls')),

    # project-level urls
    url(r'^$', 'ids.views.homepage', name='homepage'),

    # auth
    url(r'^auth/', include('ids_auth.urls', namespace='ids_auth')),
    url(r'^login/$', 'ids_auth.views.agave_oauth', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    # projects
    url(r'^', include('ids_projects.urls', namespace='ids_projects')),
)
