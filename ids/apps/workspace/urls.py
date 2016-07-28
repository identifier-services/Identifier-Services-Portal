from django.conf.urls import include, url, patterns

urlpatterns = patterns('ids.apps.workspace.views.api',
    url(r'^api/projects/public'), 'projects_public', name='public-projects'),
    url(r'^api/projects'), 'projects_private', name='private-projects'),
)
