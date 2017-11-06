from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    #######################
    # investigation types #
    #######################

    # list
    url(r'^investigation-types/$', 
        views.InvestigationTypeListView.as_view(), 
        name='investigation_type_list'),

    # create
    url(r'^investigation-type/create/$', 
        views.InvestigationTypeCreateView.as_view(), 
        name='investigation_type_create'),

    # detail
    url(r'^investigation-type/(?P<pk>[0-9a-f-]+)$', 
        views.InvestigationTypeDetailView.as_view(), 
        name='investigation_type_detail'),

    # update
    url(r'^investigation-type/(?P<pk>[0-9a-f-]+)/update/$', 
        views.InvestigationTypeUpdateView.as_view(), 
        name='investigation_type_update'),

    # delete
    url(r'^investigation-type/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.InvestigationTypeDeleteView.as_view(), 
        name='investigation_type_delete'),

    ###########
    # project #
    ###########

    # list
    url(r'^projects/$', 
        views.ProjectListView.as_view(), 
        name='project_list'),

    # create
    url(r'^project/create/$', 
        views.ProjectCreateView.as_view(), 
        name='project_create'),
    
    # detail
    url(r'^project/(?P<pk>[0-9a-f-]+)$', 
        views.ProjectDetailView.as_view(), 
        name='project_detail'),

    # update
    url(r'^project/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ProjectUpdateView.as_view(), 
        name='project_update'),

    # delete
    url(r'^project/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ProjectDeleteView.as_view(), 
        name='project_delete'),

    ################
    # element type #
    ################

    # list
    url(r'^element-types/$', 
        views.ElementTypeListView.as_view(), 
        name='element_type_list'),

    # create
    url(r'^element-type/create/$', 
        views.ElementTypeCreateView.as_view(), 
        name='element_type_create'),

    # detail
    url(r'^element-type/(?P<pk>[0-9a-f-]+)$', 
        views.ElementTypeDetailView.as_view(), 
        name='element_type_detail'),

    # update
    url(r'^element-type/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementTypeUpdateView.as_view(), 
        name='element_type_update'),
    # delete
    url(r'^element-type/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementTypeDeleteView.as_view(), 
        name='element_type_delete'),

    ############################
    # element field descriptor #
    ############################

    # list
    url(r'^element-field-descriptors/$', 
        views.ElementFieldDescriptorListView.as_view(), 
        name='element_field_descriptor_list'),
    
    # create
    url(r'^element-field-descriptor/create/$', 
        views.ElementFieldDescriptorCreateView.as_view(), 
        name='element_field_descriptor_create'),
    
    # detail
    url(r'^element-field-descriptor/(?P<pk>[0-9a-f-]+)$', 
        views.ElementFieldDescriptorDetailView.as_view(), 
        name='element_field_descriptor_detail'),
    
    # update
    url(r'^element-field-descriptor/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementFieldDescriptorUpdateView.as_view(), 
        name='element_field_descriptor_update'),
    
    # delete
    url(r'^element-field-descriptor/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementFieldDescriptorDeleteView.as_view(), 
        name='element_field_descriptor_delete'),

    ###########################
    # relationship definition #
    ###########################

    # list
    url(r'^relationship-definitions/$', 
        views.RelationshipDefinitionListView.as_view(), 
        name='relationship_definition_list'),

    # create
    url(r'^relationship-definition/create/$', 
        views.RelationshipDefinitionCreateView.as_view(), 
        name='relationship_definition_create'),

    # detail
    url(r'^relationship-definition/(?P<pk>[0-9a-f-]+)$', 
        views.RelationshipDefinitionDetailView.as_view(), 
        name='relationship_definition_detail'),

    # update
    url(r'^relationship-definition/(?P<pk>[0-9a-f-]+)/update/$', 
        views.RelationshipDefinitionUpdateView.as_view(), 
        name='relationship_definition_update'),
    # delete
    url(r'^relationship-definition/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.RelationshipDefinitionDeleteView.as_view(), 
        name='relationship_definition_delete'),

    ###########
    # element #
    ###########

    # list
    url(r'^elements/$', 
        views.ElementListView.as_view(), 
        name='element_list'),
    
    # create
    url(r'^element/create/$', 
        views.ElementCreateView.as_view(), 
        name='element_create'),
    
    # detail
    url(r'^element/(?P<pk>[0-9a-f-]+)$', 
        views.ElementDetailView.as_view(), 
        name='element_detail'),
    
    # update
    url(r'^element/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementUpdateView.as_view(), 
        name='element_update'),
    
    # verify
    url(r'^element/(?P<pk>[0-9a-f-]+)/verify/$',
        views.element_init_checksum, 
        name='element_init_checksum'),
    
    # publish
    url(r'^element/(?P<pk>[0-9a-f-]+)/publish/$',
        views.request_doi, 
        name='request_doi'),
    
    # delete
    url(r'^element/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementDeleteView.as_view(), 
        name='element_delete'),

    ###########
    # dataset #
    ###########

    # list
    url(r'^datasets/$', 
        views.DatasetListView.as_view(), 
        name='dataset_list'),
    
    # create
    url(r'^dataset/create/$', 
        views.DatasetCreateView.as_view(), 
        name='dataset_create'),
    
    # detail
    url(r'^dataset/(?P<pk>[0-9a-f-]+)$', 
        views.DatasetDetailView.as_view(), 
        name='dataset_detail'),
    
    # update
    url(r'^dataset/(?P<pk>[0-9a-f-]+)/update/$', 
        views.DatasetUpdateView.as_view(), 
        name='dataset_update'),
    
    # delete
    url(r'^dataset/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.DatasetDeleteView.as_view(), 
        name='dataset_delete'),

    ################
    # dataset link #
    ################

    ############################
    # element char field value #
    ############################

    # list
    url(r'^element-char-field-values/$', 
        views.ElementCharFieldValueListView.as_view(), 
        name='element_char_field_value_list'),
    
    # create
    url(r'^element-char-field-value/create/$', 
        views.ElementCharFieldValueCreateView.as_view(), 
        name='element_char_field_value_create'),
    
    # detail
    url(r'^element-char-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementCharFieldValueDetailView.as_view(), 
        name='element_char_field_value_detail'),
    
    # update
    url(r'^element-char-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementCharFieldValueUpdateView.as_view(), 
        name='element_char_field_value_update'),
    
    # delete
    url(r'^element-char-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementCharFieldValueDeleteView.as_view(), 
        name='element_char_field_value_delete'),

    ############################
    # element text field value #
    ############################

    # list
    url(r'^element-text-field-values/$', 
        views.ElementTextFieldValueListView.as_view(), 
        name='element_text_field_value_list'),
    
    # create
    url(r'^element-text-field-value/create/$', 
        views.ElementTextFieldValueCreateView.as_view(), 
        name='element_text_field_value_create'),
    
    # detail
    url(r'^element-text-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementTextFieldValueDetailView.as_view(), 
        name='element_text_field_value_detail'),
    
    # update
    url(r'^element-text-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementTextFieldValueUpdateView.as_view(), 
        name='element_text_field_value_update'),
    
    # delete
    url(r'^element-text-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementTextFieldValueDeleteView.as_view(), 
        name='element_text_field_value_delete'),

    ############################
    # element int field value #
    ############################

    # list
    url(r'^element-int-field-values/$', 
        views.ElementIntFieldValueListView.as_view(), 
        name='element_int_field_value_list'),
    
    # create
    url(r'^element-int-field-value/create/$', 
        views.ElementIntFieldValueCreateView.as_view(), 
        name='element_int_field_value_create'),
    
    # detail
    url(r'^element-int-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementIntFieldValueDetailView.as_view(), 
        name='element_int_field_value_detail'),
    
    # update
    url(r'^element-int-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementIntFieldValueUpdateView.as_view(), 
        name='element_int_field_value_update'),
    
    # delete
    url(r'^element-int-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementIntFieldValueDeleteView.as_view(), 
        name='element_int_field_value_delete'),

    ############################
    # element float field value #
    ############################

    # list
    url(r'^element-float-field-values/$', 
        views.ElementFloatFieldValueListView.as_view(), 
        name='element_float_field_value_list'),
    
    # create
    url(r'^element-float-field-value/create/$', 
        views.ElementFloatFieldValueCreateView.as_view(), 
        name='element_float_field_value_create'),
    
    # detail
    url(r'^element-float-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementFloatFieldValueDetailView.as_view(), 
        name='element_float_field_value_detail'),
    
    # update
    url(r'^element-float-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementFloatFieldValueUpdateView.as_view(), 
        name='element_float_field_value_update'),
    
    # delete
    url(r'^element-float-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementFloatFieldValueDeleteView.as_view(), 
        name='element_float_field_value_delete'),

    ############################
    # element date field value #
    ############################

    # list
    url(r'^element-date-field-values/$', 
        views.ElementDateFieldValueListView.as_view(), 
        name='element_date_field_value_list'),
    
    # create
    url(r'^element-date-field-value/create/$', 
        views.ElementDateFieldValueCreateView.as_view(), 
        name='element_date_field_value_create'),
    
    # detail
    url(r'^element-date-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementDateFieldValueDetailView.as_view(), 
        name='element_date_field_value_detail'),
    
    # update
    url(r'^element-date-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementDateFieldValueUpdateView.as_view(), 
        name='element_date_field_value_update'),
    
    # delete
    url(r'^element-date-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementDateFieldValueDeleteView.as_view(), 
        name='element_date_field_value_delete'),

    ############################
    # element url field value  #
    ############################

    # list
    url(r'^element-url-field-values/$', 
        views.ElementUrlFieldValueListView.as_view(), 
        name='element_url_field_value_list'),
    
    # create
    url(r'^element-url-field-value/create/$', 
        views.ElementUrlFieldValueCreateView.as_view(), 
        name='element_url_field_value_create'),
    
    # detail
    url(r'^element-url-field-value/(?P<pk>[0-9a-f-]+)$', 
        views.ElementUrlFieldValueDetailView.as_view(), 
        name='element_url_field_value_detail'),
    
    # update
    url(r'^element-url-field-value/(?P<pk>[0-9a-f-]+)/update/$', 
        views.ElementUrlFieldValueUpdateView.as_view(), 
        name='element_url_field_value_update'),
    
    # delete
    url(r'^element-url-field-value/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ElementUrlFieldValueDeleteView.as_view(), 
        name='element_url_field_value_delete'),

    
    ########
    # path #
    ########

    # # list
    # url(r'^paths/$', 
    #     views.PathListView.as_view(), 
    #     name='path_list'),

    # # detail
    # url(r'^path/(?P<pk>[0-9a-f-]+)$', 
    #     views.PathDetailView.as_view(), 
    #     name='path_detail'),

    ###############
    # path member #
    ###############

    ############
    # checksum #
    ############

    # list
    url(r'^checksums/$', 
        views.ChecksumListView.as_view(), 
        name='checksum_list'),
    
    # create
    url(r'^checksum/create/$', 
        views.ChecksumCreateView.as_view(), 
        name='checksum_create'),
    
    # detail
    url(r'^checksum/(?P<pk>[0-9a-f-]+)$', 
        views.ChecksumDetailView.as_view(), 
        name='checksum_detail'),
    
    # update
    #url(r'^checksum/(?P<pk>[0-9a-f-]+)/update/$', 
    #    views.ChecksumUpdateView.as_view(), 
    #    name='checksum_update'),

    url(r'^checksum/(?P<pk>[0-9a-f-]+)/update/$', 
        views.checksum_update, 
        name='checksum_update'),
    
    # delete
    url(r'^checksum/(?P<pk>[0-9a-f-]+)/delete/$', 
        views.ChecksumDeleteView.as_view(), 
        name='checksum_delete'),
]
