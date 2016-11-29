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
    # relate data to an existing process
    url(r'^data/add_relationship/(?P<data_uuid>.+?)$', 'add_relationship', name='relate-data-to-process'),
    # delete a data metadata object associated with a file or sra
    url(r'^data/delete/(?P<data_uuid>.+?)$', 'data_delete', name='data-delete'),
    # edit data info
    url(r'^data/edit/(?P<data_uuid>.+?)$', 'edit', name='data-edit'),
    # do checksum
    url(r'^data/checksum/(?P<data_uuid>.+?)$', 'do_checksum', name='data-checksum'),
    # request identifier
    url(r'^data/request/(?P<id_type>.+?)/(?P<data_uuid>.+?)$', 'request_id', name='data-request-id'),
    # list data for project
    url(r'^data/list/?$', 'list', name='data-list'),
    # add image under imaging-genetics project
    url(r'^data/add_images/?$', 'add_images', name='add-images'),
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
    url(r'^dataset/request_ark/(?P<dataset_uuid>.+?)$', 'request_ark', name='dataset-request-ark'),
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
    # create a process related to a specimen
    url(r'^process/create/?$', 'create', name='process-create'),
    # edit a process
    url(r'^process/edit/(?P<process_uuid>.+?)$', 'edit', name='process-edit'),
    # relate process to an existing specimen
    url(r'^process/add_relationship/(?P<process_uuid>.+?)$', 'add_relationship', name='relate-process-to-specimen'),
    # delete a process
    url(r'^process/delete/(?P<process_uuid>.+?)$', 'delete', name='process-delete'),
    # view a process
    url(r'^process/(?P<process_uuid>.+?)$', 'view', name='process-view'),
)

###################
# Material Entity #
###################
urlpatterns += patterns(
    'ids_projects.views.material',
    # create a material entity related to a specimen
    url(r'^material/create/?$', 'create', name='material-create'),
    # edit a material entity
    url(r'^material/edit/(?P<material_uuid>.+?)$', 'edit', name='material-edit'),
    # relate material entity to an existing specimen
    url(r'^material/add_relationship/(?P<material_uuid>.+?)$', 'add_relationship', name='relate-material-to-process'),
    # delete a material entity
    url(r'^material/delete/(?P<material_uuid>.+?)$', 'delete', name='material-delete'),
    # view a material entity
    url(r'^material/(?P<material_uuid>.+?)$', 'view', name='material-view'),
)

###################
# Information Entity #
###################
urlpatterns += patterns(
    'ids_projects.views.information',
    # create a information entity related to a specimen
    url(r'^information/create/?$', 'create', name='information-create'),
    # edit a information entity
    url(r'^information/edit/(?P<information_uuid>.+?)$', 'edit', name='information-edit'),
    # relate information entity to an existing specimen
    url(r'^information/add_relationship/(?P<information_uuid>.+?)$', 'add_relationship', name='relate-information-to-process'),
    # delete a information entity
    url(r'^information/delete/(?P<information_uuid>.+?)$', 'delete', name='information-delete'),
    # view a information entity
    url(r'^information/(?P<information_uuid>.+?)$', 'view', name='information-view'),
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
    # choose upload option for specimens
    url(r'^specimen/upload_option/?$', 'upload_option', name='specimen-upload-option'),
    # edit a specimen
    url(r'^specimen/edit/(?P<specimen_uuid>.+?)$', 'edit', name='specimen-edit'),
    # delete a specimen
    url(r'^specimen/delete/(?P<specimen_uuid>.+?)$', 'delete', name='specimen-delete'),
    # view a specimen
    url(r'^specimen/(?P<specimen_uuid>.+?)$', 'view', name='specimen-view'),
)

#############
# Probes #
#############
urlpatterns += patterns(
    'ids_projects.views.probes',
    # choose upload option for probes
    url(r'probes/upload_option/?$', 'upload_option', name='probe-upload-option'),
    # create a probe
    url(r'^probes/create/?$', 'create', name='probe-create'),
    # edit a specimen
    url(r'^probes/edit/(?P<probe_uuid>.+?)$', 'edit', name='probe-edit'),
    # delete a specimen
    url(r'^probe/delete/(?P<probe_uuid>.+?)$', 'delete', name='probe-delete'),
    # view a probe
    url(r'^probe/(?P<probe_uuid>.+?)$', 'view', name='probe-view'),
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

##############
# APIs for angular
##############
urlpatterns += patterns(
    'ids_projects.views.apis',    
    url(r'^angular/(?P<entity>.+?)/(?P<uuid>.+?)/$', 'view', name='view'),
    url(r'^api/entity_detail/(?P<uuid>.+?)/$', 'entity_detail_api', name='entity-detail-api'),

    # url(r'^api/project_api/(?P<project_uuid>.+?)/$', 'project_api', name='project-api'),
    # url(r'^api/specimen_api/(?P<specimen_uuid>.+?)/$', 'specimen_api', name='specimen-api'),
    # url(r'^api/process_api/(?P<process_uuid>.+?)/$', 'process_api', name='process-api'),
    # url(r'^api/dataset_api/(?P<dataset_uuid>.+?)/$', 'dataset_api', name='dataset-api'),
    # url(r'^api/data_api/(?P<data_uuid>.+?)/$', 'data_api', name='data-api'),

    url(r'^api/get_parts/(?P<name>.+?)/(?P<uuid>.+?)/(?P<offset>.+?)$', 'get_parts_api', name='get-parts-api'),
    url(r'^api/get_inputs/(?P<uuid>.+?)/(?P<offset>.+?)$', 'get_inputs_api', name='get-inputs-api'),
    url(r'^api/get_outputs/(?P<uuid>.+?)/(?P<offset>.+?)$', 'get_outputs_api', name='get-outputs-api'),
    url(r'^api/get_inputs_to/(?P<uuid>.+?)/(?P<offset>.+?)$', 'get_inputs_to_api', name='get-inputs-to-api'),
    url(r'^api/get_outputs_of/(?P<uuid>.+?)/(?P<offset>.+?)$', 'get_outputs_of_api', name='get-outputs-of-api'),
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
    # create a datasets related to a specimen
    url(r'^identifier/create/(?P<dataset_uuid>.+?)$', 'create', name='identifier-request-doi'),
    # detail
    url(r'^identifier/(?P<identifier_uuid>.+?)$', 'view', name='identifier-view'),
)

##############
# Scheduler ##
##############
urlpatterns += patterns(
    'ids_projects.views.scheduler',
    url(r'^check/?$', 'check', name='location-check'),
)
