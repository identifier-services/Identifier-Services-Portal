from django.conf.urls import patterns, include, url


########
# Data #
########
urlpatterns = patterns(
    'ids_projects.views.data',
    # intermediate step between adding and sra or a file
    url(r'^data/type_select/?$', 'type_select', name='data-type'),
    # create a file metadata object associated with an SRA
    url(r'^data/add_sra/(?P<relationship>.+?)$', 'add_sra', name='add-sra'),
    # create a file metadata object associated with a process
    url(r'^file/select/(?P<relationship>.+?)$', 'file_select', name='file-select'),
    # list content at given path on system
    url(r'^dir/list/(?P<system_id>[^/]+)/(?P<file_path>.+)?', 'dir_list', name='dir-list'),
    # delete a data metadata object associated with a process
    url(r'^data/delete/(?P<data_uuid>.+?)$', 'data_delete', name='data-delete'),
    # edit data info
    url(r'^data/edit/(?P<data_uuid>.+?)$', 'edit', name='data-edit'),
    # do checksum
    url(r'^data/checksum/(?P<data_uuid>.+?)$', 'do_checksum', name='data-checksum'),
    # request identifier
    url(r'^data/request/(?P<id_type>.+?)/(?P<data_uuid>.+?)$', 'request_id', name='data-request-id'),
    # list data for project
    url(r'^data/list/?$', 'list', name='data-list'),
    # view data info
    url(r'^data/(?P<data_uuid>.+?)$', 'view', name='data-view'),
)

############
# Datasets #
############
urlpatterns += patterns(
    'ids_projects.views.datasets',
    # list all datasets related to a specimen
    url(r'^datasets/public?$', 'list_public', name='dataset-list-public'),
    # list all datasets related to a specimen
    url(r'^datasets/private?$', 'list_private', name='dataset-list-private'),
    # create a datasets related to a specimen
    url(r'^dataset/create/?$', 'create', name='dataset-create'),
    # edit a dataset
    url(r'^dataset/edit/(?P<dataset_uuid>.+?)$', 'edit', name='dataset-edit'),
    # delete a dataset
    url(r'^dataset/delete/(?P<dataset_uuid>.+?)$', 'delete', name='dataset-delete'),
    # select data
    url(r'^dataset/select_data/(?P<dataset_uuid>.+?)$', 'select_data', name='dataset-select-data'),
    # add data to dataset
    url(r'^dataset/add_data/(?P<dataset_uuid>.+?)$', 'add_data', name='dataset-add-data'),
    # remove data from dataset
    url(r'^dataset/remove_data/(?P<dataset_uuid>.+?)$', 'remove_data', name='dataset-remove-data'),
    # make dataset public
    url(r'^project/make_public/(?P<dataset_uuid>.+?)$', 'make_public', name='dataset-make-public'),
    # make dataset private
    url(r'^project/make_private/(?P<dataset_uuid>.+?)$', 'make_private', name='dataset-make-private'),
    # request doi for public dataset
    url(r'^dataset/request_doi/(?P<dataset_uuid>.+?)$', 'request_doi', name='dataset-request-doi'),
    # view a process
    url(r'^dataset/(?P<dataset_uuid>.+?)$', 'view', name='dataset-view'),
)

###########
# Systems #
###########
urlpatterns += patterns(
    'ids_projects.views.systems',
    # list all systems available to user
    url(r'^systems/?$', 'list', name='system-list'),
    # # register a system
    # url(r'^system/register/?$', 'create', name='system-create'),
    # # edit a system
    # url(r'^system/edit/(?P<system_id>.+?)$', 'edit', name='system-edit'),
    # # unregister a system
    # url(r'^system/delete/(?P<system_id>.+?)$', 'delete', name='system-delete'),
    # # view a system
    # url(r'^system/(?P<system_id>.+?)$', 'view', name='system-view'),
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
    # list private projects
    url(r'^projects/?$', 'list_private', name='project-list-private'),
    # # list all projects
    # url(r'^projects/?$', 'list', name='project-list-private'),
    # create project
    url(r'^project/create/?$', 'create', name='project-create'),
    # edit project
    url(r'^project/edit/(?P<project_uuid>.+?)$', 'edit', name='project-edit'),
    # delete project
    url(r'^project/delete/(?P<project_uuid>.+?)$', 'delete', name='project-delete'),
    # view a specific project
    url(r'^project/(?P<project_uuid>.+?)$', 'view', name='project-view'),
)

############
# Webhooks #
############
urlpatterns += patterns(
    'ids_projects.webhooks',
    url(r'webhook/(?P<hook_type>\w+)/?$', 'handle_webhook', name='webhook'),
)

###############
# Identifiers #
###############
urlpatterns += patterns(
    'ids_projects.views.identifiers',
    url(r'^identifier/(?P<identifier_uuid>.+?)$', 'view', name='identifier-view'),
)