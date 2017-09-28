# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

import logging

from zipfile import ZipFile
import csv

from .models import (InvestigationType, Project, ElementType,
    RelationshipDefinition, ElementFieldDescriptor, Element, Dataset,
    ElementCharFieldValue, ElementTextFieldValue, ElementIntFieldValue,
    ElementFloatFieldValue, ElementDateFieldValue, ElementUrlFieldValue)

from .forms import ProjectForm

logger = logging.getLogger(__name__)

##############
# Base Views #
##############

class BaseGenericListView(generic.ListView):
    template_name = 'app/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        logger.debug('request user: %s' % self.request.user)
        logger.debug('dir(request.user): %s' % dir(self.request.user))

        context = super(BaseGenericListView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['verbose_name'] = verbose_name.title()
        context['type_name'] = verbose_name.replace(' ', '_')
        context['create_url'] = self.model.get_create_url()
        return context


class BaseGenericDetailView(generic.DetailView):
    template_name = 'app/generic_detail.html'
    context_object_name = 'object'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(BaseGenericDetailView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['verbose_name'] = verbose_name.title()
        context['type_name'] = verbose_name.replace(' ', '_')

        #context_object = context['object']
        #child_rels_group = context_object.get_child_relations()

        #page = self.request.GET.get('page')

        #paginators = []
        #for child_rel_group in child_rels_group:
        #    pag = paginator.Paginator(child_rel_group['objects'], self.paginate_by)
        #    try:
        #        paginators.append(pag.page(page))
        #    except:
        #        paginators.append(pag.page(1))

        #context['page_objs'] = paginators

        return context


class BaseGenericCreateView(generic.CreateView):
    template_name = 'app/generic_form.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(BaseGenericCreateView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['verbose_name'] = verbose_name.title()
        context['type_name'] = verbose_name.replace(' ', '_')
        return context

    def get_initial(self):
        parent_qs = self.request.GET.get('parent')
        initial = {}

        if parent_qs:
            parent_types = self.model.get_parent_types()
            if not parent_types:
                return None

            for parent in parent_qs.split(','):
                try:
                    parent_name, parent_id = parent.split(':')
                    parent_class = filter(
                        lambda x,y=parent_name: x['field_name'] == parent_name,
                        parent_types).pop().get('class')

                    initial.update({
                        parent_name: parent_class.objects.get(pk=parent_id)
                    })
                except Exception as e:
                    logger.debug(e)

        return initial


class BaseGenericUpdateView(generic.UpdateView):
    template_name = 'app/generic_form.html'
    context_object_name = 'object'
    fields = '__all__'


class BaseGenericDeleteView(generic.DeleteView):
    template_name = 'app/generic_delete.html'
    context_object_name = 'object'

    # the success url is difficult to determine, it's going to get
    # complicated with anything other than project or investigation lists
    success_url = reverse_lazy('app:project_list')

    def get_context_data(self, **kwargs):
        context = super(BaseGenericDeleteView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['type_name'] = verbose_name

        # set the success_url to the parent, if there is one.
        # this is hacky, but then the whole thing is
        context_object = context['object']
        parent_rels = context_object.get_parent_relations()
        if parent_rels:

            # just get the first parent
            parent_rel = next(iter(parent_rels))

            try:
                success_url = reverse('%s_detail' % parent_rel['field_name'])
            except Exception as e:
                logger.debug(e)

        return context

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            url = self.success_url
            if not url:
                url = reverse('app:project_list')
            return HttpResponseRedirect(url) 
        else:
            return super(BaseGenericDeleteView, self).post(
                request, *args, **kwargs)

#############
# Home Page #
#############

def index(request):
    """home page"""
    return render (request, 'app/index.html', context={})

######################
# Investigation Type #
######################

class InvestigationTypeListView(BaseGenericListView):
    model = InvestigationType


class InvestigationTypeCreateView(BaseGenericCreateView):
    model = InvestigationType


class InvestigationTypeDetailView(BaseGenericDetailView):
    model = InvestigationType


class InvestigationTypeUpdateView(BaseGenericUpdateView):
    model = InvestigationType
    fields = '__all__'


class InvestigationTypeDeleteView(BaseGenericDeleteView):
    model = InvestigationType
    # success_url = reverse('app:index')

###########
# Project #
###########

class ProjectListView(BaseGenericListView):
    model = Project


class ProjectCreateView(BaseGenericCreateView):
    model = Project


class ProjectDetailView(BaseGenericDetailView):
    model = Project


class ProjectUpdateView(BaseGenericUpdateView):
    model = Project


class ProjectDeleteView(BaseGenericDeleteView):
    model = Project

################
# Element Type #
################

class ElementTypeListView(BaseGenericListView):
    model = ElementType


class ElementTypeCreateView(BaseGenericCreateView):
    model = ElementType


class ElementTypeDetailView(BaseGenericDetailView):
    model = ElementType


class ElementTypeUpdateView(BaseGenericUpdateView):
    model = ElementType


class ElementTypeDeleteView(BaseGenericDeleteView):
    model = ElementType


############################
# Element Field Descriptor #
############################

class ElementFieldDescriptorListView(BaseGenericListView):
    model = ElementFieldDescriptor


class ElementFieldDescriptorCreateView(BaseGenericCreateView):
    model = ElementFieldDescriptor
    fields = '__all__'


class ElementFieldDescriptorDetailView(generic.DetailView):
    model = ElementFieldDescriptor
    template_name = 'app/field_descriptor_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ElementFieldDescriptorDetailView, self)\
            .get_context_data(**kwargs)
        descriptor = context['object']

        try:
            context['value_type'] = descriptor.verbose_value_type
        except Exception as e:
            logger.debug(e)

        return context


class ElementFieldDescriptorUpdateView(BaseGenericUpdateView):
    model = ElementFieldDescriptor


class ElementFieldDescriptorDeleteView(BaseGenericDeleteView):
    model = ElementFieldDescriptor

###########################
# Relationship Definition #
###########################

class RelationshipDefinitionListView(BaseGenericListView):
    model = RelationshipDefinition


class RelationshipDefinitionCreateView(BaseGenericCreateView):
    model = RelationshipDefinition
    fields = '__all__'


class RelationshipDefinitionDetailView(generic.DetailView):
    model = RelationshipDefinition
    template_name = 'app/relationship_definition_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RelationshipDefinitionDetailView, self)\
            .get_context_data(**kwargs)
        definition = context['object']

        try:
            context['rel_type'] = definition.verbose_relationship_type
        except Exception as e:
            logger.debug(e)

        try:
            context['card'] = definition.verbose_cardinality
        except Exception as e:
            logger.debug(e)

        return context


class RelationshipDefinitionUpdateView(BaseGenericUpdateView):
    model = RelationshipDefinition


class RelationshipDefinitionDeleteView(BaseGenericDeleteView):
    model = RelationshipDefinition

###########
# Element #
###########

class ElementListView(BaseGenericListView):
    model = Element


class ElementCreateView(BaseGenericCreateView):
    model = Element


class ElementDetailView(generic.DetailView):
    model = Element
    template_name = 'app/element_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ElementDetailView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['verbose_name'] = verbose_name.title() 
        context['type_name'] = verbose_name.replace(' ', '_')

        context_object = context['object']
        descriptors = \
            context_object.element_type.elementfielddescriptor_set.filter(
                element_type__element=context_object
            )

        values = []
        for descriptor in descriptors:
            # get descriptor attributes
            label = descriptor.label
            help_text = descriptor.help_text
            
            # get the values
            value_type = descriptor.value_type

            # TODO: what if more than one field value? how to prevent?
            field_value = value_type.objects.filter(
                element = context_object,
                element_field_descriptor=descriptor
            ).first()

            if field_value:
                action_url = '%s/update' % field_value.get_absolute_url()
                action = 'Edit'
            else:
                descriptor_field_name = \
                    descriptor._meta.verbose_name.replace(' ', '_')

                parents_qs = '?parent=%s:%s,%s:%s' % (
                    descriptor_field_name, descriptor.id,
                    context['type_name'], context_object.id
                )
                action_url = '%s%s' % (value_type.get_create_url(), parents_qs)
                action = 'Set'

            type_id = descriptor.id

            values.append({
                'label': label,
                'help_text': help_text,
                'field_value': field_value,
                'action_url': action_url,
                'action': action,
            })
        context['values'] = values

        # import pdb; pdb.set_trace()

        return context


class ElementUpdateView(BaseGenericUpdateView):
    model = Element


class ElementDeleteView(BaseGenericDeleteView):
    model = Element

###########
# Dataset #
###########

class DatasetListView(BaseGenericListView):
    model = Dataset


class DatasetCreateView(BaseGenericCreateView):
    model = Dataset


class DatasetDetailView(BaseGenericDetailView):
    model = Dataset
    template_name = 'app/dataset_detail.html'

    def get_context_data(self, **kwargs):
        context = super(DatasetDetailView, self).get_context_data(**kwargs)
        verbose_name = self.model._meta.verbose_name
        context['verbose_name'] = verbose_name.title() 
        context['type_name'] = verbose_name.replace(' ', '_')

        context_object = context['object']

        return context

class DatasetUpdateView(BaseGenericUpdateView):
    model = Dataset


class DatasetDeleteView(BaseGenericDeleteView):
    model = Dataset

############################
# Element Char Field Value #
############################

class ElementCharFieldValueListView(BaseGenericListView):
    model = ElementCharFieldValue


class ElementCharFieldValueCreateView(BaseGenericCreateView):
    model = ElementCharFieldValue


class ElementCharFieldValueDetailView(BaseGenericDetailView):
    model = ElementCharFieldValue


class ElementCharFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementCharFieldValue


class ElementCharFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementCharFieldValue


############################
# Element Text Field Value #
############################

class ElementTextFieldValueListView(BaseGenericListView):
    model = ElementTextFieldValue


class ElementTextFieldValueCreateView(BaseGenericCreateView):
    model = ElementTextFieldValue


class ElementTextFieldValueDetailView(BaseGenericDetailView):
    model = ElementTextFieldValue


class ElementTextFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementTextFieldValue


class ElementTextFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementTextFieldValue

############################
# Element Int Field Value #
############################

class ElementIntFieldValueListView(BaseGenericListView):
    model = ElementIntFieldValue


class ElementIntFieldValueCreateView(BaseGenericCreateView):
    model = ElementIntFieldValue


class ElementIntFieldValueDetailView(BaseGenericDetailView):
    model = ElementIntFieldValue


class ElementIntFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementIntFieldValue


class ElementIntFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementIntFieldValue

#############################
# Element Float Field Value #
#############################

class ElementFloatFieldValueListView(BaseGenericListView):
    model = ElementFloatFieldValue


class ElementFloatFieldValueCreateView(BaseGenericCreateView):
    model = ElementFloatFieldValue


class ElementFloatFieldValueDetailView(BaseGenericDetailView):
    model = ElementFloatFieldValue


class ElementFloatFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementFloatFieldValue


class ElementFloatFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementFloatFieldValue

############################
# Element Date Field Value #
############################

class ElementDateFieldValueListView(BaseGenericListView):
    model = ElementDateFieldValue


class ElementDateFieldValueCreateView(BaseGenericCreateView):
    model = ElementDateFieldValue


class ElementDateFieldValueDetailView(BaseGenericDetailView):
    model = ElementDateFieldValue


class ElementDateFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementDateFieldValue


class ElementDateFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementDateFieldValue

############################
# Element Url Field Value  #
############################

class ElementUrlFieldValueListView(BaseGenericListView):
    model = ElementUrlFieldValue


class ElementUrlFieldValueCreateView(BaseGenericCreateView):
    model = ElementUrlFieldValue


class ElementUrlFieldValueDetailView(BaseGenericDetailView):
    model = ElementUrlFieldValue


class ElementUrlFieldValueUpdateView(BaseGenericUpdateView):
    model = ElementUrlFieldValue


class ElementUrlFieldValueDeleteView(BaseGenericDeleteView):
    model = ElementUrlFieldValue
