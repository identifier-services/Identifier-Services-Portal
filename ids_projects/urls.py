from django.conf.urls import patterns, include, url

# urlpatterns = patterns('')

#########
# Files #
#########
# urlpatterns = patterns(
#     'ids_projects.views.files',
#     # list all files associated with a process
#     url(r'^process/(?P<process_uuid>.+)/files/?$', 'list', name='files-list'),
#     # create a file metadata object associated with a process
#     url(r'^process/(?P<process_uuid>.+)/file/?$', 'create', name='files-create'),
#     # edit a file metadata object
#     url(r'^file/(?P<data_id>.+)/edit$', 'edit', name='files-edit'),
#     # edit a file metadata object
#     url(r'^file/(?P<data_id>.+)/delete$', 'delete', name='files-delete'),
#     # view a file metadata object
#     url(r'^file/(?P<data_id>.+)/?$', 'view', name='files-view'),
# )

urlpatterns = patterns(
    'ids_projects.views.files',
    # # list all files associated with a process
    # url(r'^process/(?P<process_uuid>.+?)/files/?$', 'list', name='files-list'),
    # create a file metadata object associated with a process
    # url(r'^process/(?P<process_uuid>.+?)/file/?$', 'add_data', name='add_data'),
    url(r'^data/create/?$', 'add_data', name='add-data'),
    # # edit a file metadata object
    # url(r'^file/(?P<data_id>.+?)/edit$', 'edit', name='files-edit'),
    # # edit a file metadata object
    # url(r'^file/(?P<data_id>.+?)/delete$', 'delete', name='files-delete'),
    # # view a file metadata object
    # url(r'^file/(?P<data_id>.+)/?$', 'view', name='files-view'),
    ############################################################################
    # list content at given path on system
    # url(r'^system/(?P<system_id>.+?)/listing/(?P<path>.+)$', 'listing', name='systems-listing'),
    # url(r'^listing/(?P<system_id>[^/]+)/(?P<file_path>.+)?', 'files_list', name='files_list_json'),
    url(r'^listing/(?P<system_id>[^/]+)/(?P<file_path>.+)?', 'files_list', name='files-list'),
    ############################################################################
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
    url(r'^process/edit/(?P<process_uuid>.+?)/?$', 'edit', name='process-edit'),
    # delete a process
    url(r'^process/delete/(?P<process_uuid>.+?)/?$', 'delete', name='process-delete'),
    # view a process
    url(r'^process/(?P<process_uuid>.+?)/?$', 'view', name='process-view'),
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
    url(r'^specimen/edit/(?P<specimen_uuid>.+?)/$', 'edit', name='specimen-edit'),
    # delete a specimen
    url(r'^specimen/delete/(?P<specimen_uuid>.+?)/$', 'delete', name='specimen-delete'),
    # view a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/?$', 'view', name='specimen-view'),
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
    url(r'^project/edit/(?P<project_uuid>.+?)/?$', 'edit', name='project-edit'),
    # delete project
    url(r'^project/delete/(?P<project_uuid>.+?)/?$', 'delete', name='project-delete'),
    # view a specific project
    url(r'^project/(?P<project_uuid>.+?)/?$', 'view', name='project-view'),
)
