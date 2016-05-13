from django.conf.urls import patterns, include, url


#########
# Files #
#########
urlpatterns = patterns(
    'ids_projects.views.data',
    # create a file metadata object associated with a process
    url(r'^file/select/?$', 'file_select', name='file-select'),
    # list content at given path on system
    url(r'^dir/list/(?P<system_id>[^/]+)/(?P<file_path>.+)?', 'dir_list', name='dir-list'),
    # delete a data metadata object associated with a process
    url(r'^data/delete/(?P<data_uuid>.+?)$', 'data_delete', name='data-delete'),
)


###########
# Systems #
###########
urlpatterns += patterns(
    'ids_projects.views.systems',
    # list all systems available to user
    url(r'^systems/?$', 'list', name='system-list'),
    # register a system
    url(r'^system/register/?$', 'create', name='system-create'),
    # edit a system
    url(r'^system/edit/(?P<system_id>.+?)$', 'edit', name='system-edit'),
    # unregister a system
    url(r'^system/delete/(?P<system_id>.+?)$', 'delete', name='system-delete'),
    # view a system
    url(r'^system/(?P<system_id>.+?)$', 'view', name='system-view'),
)


#############
# Processes #
#############
urlpatterns += patterns(
    'ids_projects.views.processes',
    # list all processes related to a specimen
    url(r'^processes/?$', 'list', name='process-list'),
    # create a processes related to a specimen
    url(r'^process/create/?$', 'create', name='process-create'),
    # edit a process
    url(r'^process/edit/(?P<process_uuid>.+?)$', 'edit', name='process-edit'),
    # delete a process
    url(r'^process/delete/(?P<process_uuid>.+?)$', 'delete', name='process-delete'),
    # view a process
    url(r'^process/(?P<process_uuid>.+?)$', 'view', name='process-view'),
)


#############
# Specimens #
#############
urlpatterns += patterns(
    'ids_projects.views.specimens',
    # list all specimens related to a project, view takes project_uuid query parameter
    # TODO: this route/view (specimen-list) isn't used in the application, remove?
    # or respond with json instead of html?
    url(r'^specimens/?$', 'list', name='specimen-list'),
    # create a specimen related to a project, view takes project_uuid query parameter
    url(r'^specimen/create/?$', 'create', name='specimen-create'),
    # edit a specimen
    url(r'^specimen/edit/(?P<specimen_uuid>.+?)$', 'edit', name='specimen-edit'),
    # delete a specimen
    url(r'^specimen/delete/(?P<specimen_uuid>.+?)$', 'delete', name='specimen-delete'),
    # view a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)$', 'view', name='specimen-view'),
)


############
# Projects #
############
urlpatterns += patterns(
    'ids_projects.views.projects',
    # list all projects
    url(r'^projects/?$', 'list', name='project-list'),
    # create project
    url(r'^project/create/?$', 'create', name='project-create'),
    # edit project
    url(r'^project/edit/(?P<project_uuid>.+?)$', 'edit', name='project-edit'),
    # delete project
    url(r'^project/delete/(?P<project_uuid>.+?)$', 'delete', name='project-delete'),
    # view a specific project
    url(r'^project/(?P<project_uuid>.+?)$', 'view', name='project-view'),
)

####
# Webhooks
####
urlpatterns += patterns(
    'ids_projects.webhooks',
    url(r'webhook/(?P<hook_type>\w+)/?$', 'handle_webhook', name='webhook'),
)
