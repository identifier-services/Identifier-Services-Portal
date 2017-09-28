from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.login_prompt, name='login'),
    # url(r'^login/$', views.agave_oauth, name='login'),
    # url(r'^logout/$', views.logout, {'next_page': '/'}, name='logout'),
    url(r'^agave/$', views.agave_oauth, name='agave_oauth'),
    url(r'^agave/callback/$', views.agave_oauth_callback, name='agave_oauth_callback'),
] 
