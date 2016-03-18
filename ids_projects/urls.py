from django.conf.urls import patterns, include, url

# urlpatterns = patterns('')

#########
# Files #
#########
# urlpatterns = patterns(
#     'ids_projects.views.files',
#     # list all files associated with a process
#     url(r'^process/(?P<process_uuid>.+)/files/?$', 'list', name='files-list'),
#     # create a file metadat object associated with a process
#     url(r'^process/(?P<process_uuid>.+)/file/?$', 'create', name='files-create'),
#     # edit a file metadata object
#     url(r'^file/(?P<data_id>.+)/edit$', 'edit', name='files-edit'),
#     # edit a file metadata object
#     url(r'^file/(?P<data_id>.+)/delete$', 'delete', name='files-delete'),
#     # view a file metadata object
#     url(r'^file/(?P<data_id>.+)/?$', 'view', name='files-view'),
# )

#############
# Processes #
#############
urlpatterns = patterns(
    'ids_projects.views.processes',
    # list all processes related to a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/processes/?$', 'list', name='processes-list'),
    # create a processes related to a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/process/?$', 'create', name='processes-create'),
    # edit a process
    url(r'^process/(?P<process_uuid>.+?)/edit$', 'edit', name='processes-edit'),
    # delete a process
    url(r'^process/(?P<process_uuid>.+?)/delete$', 'delete', name='processes-delete'),
    # view a process
    url(r'^process/(?P<process_uuid>.+?)/?$', 'view', name='processes-view'),
)

###########
# Systems #
########### # TODO: may create another app for systems
# urlpatterns += patterns(
#     'ids_projects.views.systems',
#     url(r'^project/(?P<project_uuid>.+)/systems/?$', 'index', name='index'),
#     url(r'^project/(?P<project_uuid>.+)/system/(?P<system_id>.+)/?$', 'detail', name='detail'),
#     url(r'^project/(?P<project_uuid>.+)/system/?$', 'detail', name='detail'),
# )

#############
# Workflows #
############# # TODO: create another app for workflows (maybe?)
# urlpatterns += patterns(
#     'ids_projects.views.workflows',
#     # list workflows associated with a project
#     url(r'^project/(?P<project_uuid>.+)/workflows/?$', 'list', name='workflows-list'),
#     # create a worflow associated with a project
#     url(r'^project/(?P<project_uuid>.+)/workflow/?$', 'create', name='workflows-create'),
#     # edit a workflow
#     url(r'^workflow/(?P<workflow_id>.+)/edit$', 'edit', name='workflows-edit'),
#     # delete a workflow
#     url(r'^workflow/(?P<workflow_id>.+)/delete$', 'delete', name='workflows-delete'),
#     # view a workflow
#     url(r'^workflow/(?P<workflow_id>.+)/?$', 'view', name='workflows-view'),
# )

#############
# Specimens #
#############
urlpatterns += patterns(
    'ids_projects.views.specimens',
    # list all specimens related to a project
    url(r'^project/(?P<project_uuid>.+?)/specimens/?$', 'list', name='specimens-list'),
    # create a specimen related to a project
    url(r'^project/(?P<project_uuid>.+?)/specimen/?$', 'create', name='specimens-create'),
    # edit a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/edit$', 'edit', name='specimens-edit'), # or specimen_edit/...?
    # delete a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/delete$', 'delete', name='specimens-delete'), # or specimen_delete/...?
    # view a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)/?$', 'view', name='specimens-view'),
)

############
# Projects #
############
urlpatterns += patterns(
    'ids_projects.views.projects',
    # list all projects
    url(r'^projects/?$', 'list', name='projects-list'),
    # create project
    url(r'^project/?$', 'create', name='projects-create'),
    # edit project
    url(r'^project/(?P<project_uuid>.+?)/edit$', 'edit', name='projects-edit'), # or project_edit/... ?
    # delete project
    url(r'^project/(?P<project_uuid>.+?)/delete$', 'delete', name='projects-delete'), # or project_delete/... ?
    # view a specific project
    url(r'^project/(?P<project_uuid>.+?)/?$', 'view', name='projects-view'),
)
