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

    # projects
    # url(r'^projects/', include('ids_projects.urls', namespace='ids_projects')),
    #
    # # specimens
    # url(r'^specimens/', include('ids_specimens.urls', namespace='ids_specimens')),
    #
    # # datasets
    # url(r'^datasets/', include('ids_datasets.urls', namespace='ids_datasets')),
    #
    # # datasets
    # url(r'^data/', include('ids_data.urls', namespace='ids_data')),
    #
    # # systems
    # url(r'^systems/', include('ids_systems.urls', namespace='ids_systems')),

    # auth
    url(r'^auth/', include('ids_auth.urls', namespace='ids_auth')),
    url(r'^login/$', 'ids_auth.views.agave_oauth', name='login'),
    url(r'^logout/$','django.contrib.auth.views.logout', { 'next_page': '/' }, name='logout'),
    # url(r'^', include('ids_auth.urls', namespace='ids_auth')),

    # projects
    url(r'^', include('ids_projects.urls', namespace='ids_projects')),
)
