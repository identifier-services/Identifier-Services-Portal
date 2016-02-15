from django.conf.urls import patterns, include, url

urlpatterns = patterns('ids_auth.views',
    url(r'^$', 'login_prompt', name='login'),
    url(r'^agave/$', 'agave_oauth', name='agave_oauth'),
    url(r'^agave/callback/$', 'agave_oauth_callback', name='agave_oauth_callback'),
)
