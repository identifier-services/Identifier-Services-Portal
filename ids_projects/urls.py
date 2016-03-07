from django.conf.urls import patterns, include, url

#############
# Specimens #
#############
urlpatterns = patterns(
    'ids_projects.views.specimens',
    # list all specimens related to a project
    url(r'^project/(?P<project_id>.+)/specimens/?$', 'list', name='list'),
    # create a specimen related to a project
    url(r'^project/(?P<project_id>.+)/specimen/?$', 'create', name='create'),
    # view a specimen
    url(r'^specimen/(?P<specimen_id>.+)/?$', 'view', name='view'),
    # edit a specimen
    url(r'^specimen/(?P<specimen_id>.+)/edit$', 'edit', name='edit'), # or specimen_edit/...?
    # delete a specimen
    url(r'^specimen/(?P<specimen_id>.+)/delete$', 'delete', name='delete'), # or specimen_delete/...?
)

#############
# Processes #
#############
urlpatterns += patterns(
    'ids_projects.views.processes',
    # list all processes related to a specimen
    url(r'^specimen/(?P<specimen_id>.+)/processes/?$', 'list', name='list'),
    # create a processes related to a specimen
    url(r'^specimen/(?P<specimen_id>.+)/process/?$', 'create', name='create'),
    # view a process
    url(r'^process/(?P<process_id>.+)/?$', 'view', name='view'),
    # edit a process
    url(r'^process/(?P<process_id>.+)/edit$', 'edit', name='edit'),
    # delete a process
    url(r'^process/(?P<process_id>.+)/delete$', 'delete', name='delete'),
)

#########
# Files #
#########
urlpatterns += patterns(
    'ids_projects.views.files',
    # list all files associated with a process
    url(r'^process/(?P<process_id>.+)/files/?$', 'list', name='list'),
    # create a file metadat object associated with a process
    url(r'^process/(?P<process_id>.+)/file/?$', 'create', name='create'),
    # view a file metadata object
    url(r'^file/(?P<data_id>.+)/?$', 'view', name='view'),
    # edit a file metadata object
    url(r'^file/(?P<data_id>.+)/edit$', 'edit', name='edit'),
    # edit a file metadata object
    url(r'^file/(?P<data_id>.+)/delete$', 'delete', name='delete'),
)

###########
# Systems #
########### # TODO: may create another app for systems
# urlpatterns += patterns(
#     'ids_projects.views.systems',
#     url(r'^project/(?P<project_id>.+)/systems/?$', 'index', name='index'),
#     url(r'^project/(?P<project_id>.+)/system/(?P<system_id>.+)/?$', 'detail', name='detail'),
#     url(r'^project/(?P<project_id>.+)/system/?$', 'detail', name='detail'),
# )

#############
# Workflows #
############# # TODO: create another app for workflows (maybe?)
urlpatterns += patterns(
    'ids_projects.views.workflows',
    # list workflows associated with a project
    url(r'^project/(?P<project_id>.+)/workflows/?$', 'list', name='list'),
    # create a worflow associated with a project
    url(r'^project/(?P<project_id>.+)/workflow/?$', 'create', name='create'),
    # view a workflow
    url(r'^workflow/(?P<workflow_id>.+)/?$', 'view', name='view'),
    # edit a workflow
    url(r'^workflow/(?P<workflow_id>.+)/edit$', 'edit', name='edit'),
    # delete a workflow
    url(r'^workflow/(?P<workflow_id>.+)/delete$', 'delete', name='delete'),
)

############
# Projects #
############
urlpatterns += patterns(
    'ids_projects.views.projects',
    # list all projects
    url(r'^projects/?$', 'list', name='list'),
    # create project
    url(r'^project/?$', 'create', name='create'),
    # view a specific project
    url(r'^project/(?P<project_id>.+)/?$', 'view', name='view'),
    # edit project
    url(r'^project/(?P<project_id>.+)/edit$', 'edit', name='edit'), # or project_edit/... ?
    # delete project
    url(r'^project/(?P<project_id>.+)/delete$', 'delete', name='delete'), # or project_delete/... ?
)
