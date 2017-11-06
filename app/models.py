# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from agavepy.agave import Agave

from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from collections import namedtuple

import uuid
import re
import yaml
import csv
import logging

logger = logging.getLogger(__name__)

# TODO: * investigation type and project need owner & collaborators
# TODO: * they also need to be locked if an identifer has been requested
# TODO: * should we lock the whole project, only parts related to identifier?
# TODO: * if inv type is locked, and user wants to edit another project w/same
# TODO:   inv type, must clone, create a new version of inv type
# TODO: * maybe user should be able to clone project as well
# TODO: * i think we also need a public / private flag
# TODO: * all other things will inherit from project or inv type


portal_agave_client = Agave(
    api_server=settings.AGAVE_TENANT_BASEURL,
    token=settings.AGAVE_SUPER_TOKEN
)

def snake(name):
    """
    Takes camelcase string, returns string in snake case.
    https://stackoverflow.com/a/12867228
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()


class Base(object):
    """
    Provides methods for various abstract model classes.
    """ # I think it doesn't follow good practice through.

    # TODO: add is_public (queries project)
    # TODO: add owner (queries project)

    @classmethod
    def get_parent_types(self):
        fields = self._meta.get_fields()
        foreign_keys = filter(lambda x: type(x) == models.ForeignKey, fields)
        parent_types = []

        for foreign_key in foreign_keys:
            parent = getattr(self, foreign_key.name)
            parent_types.append({
                'field_name': foreign_key.name,
                'class': parent.field.related_model,
            })

        return parent_types

    def get_parent_relations(self):
        fields = self._meta.get_fields()
        foreign_keys = filter(lambda x: type(x) == models.ForeignKey, fields)
        parents = []
        for foreign_key in foreign_keys:
            parent = getattr(self, foreign_key.name)
            parents.append({
                'verbose_name': parent._meta.verbose_name,
                'object': parent,
            })

        return parents

    def get_child_relations(self):
        fields = self._meta.get_fields()
        many_to_ones = filter(lambda x: type(x) == models.ManyToOneRel, fields)
        child_relations = []
        for many_to_one in many_to_ones:        
            rm = getattr(self, many_to_one.get_accessor_name())

            child_relations.append({
                'type_name': many_to_one.related_model._meta.verbose_name,
                'objects': rm.all(),
                'create_url': many_to_one.related_model.get_create_url(),
            })

        return child_relations

    def get_fields(self):
        fields = filter(lambda x: (not x.auto_created and not x.related_model),
            self._meta.get_fields())

        field_list = []
        for field in fields:
            field_list.append({
                'label': field.verbose_name,
                'value': getattr(self, field.name),
            })

        return field_list

    def get_absolute_url(self):
        route = 'app:%s_detail' % snake(self.__class__.__name__)
        return reverse(route, args=[str(self.id)])

    @classmethod
    def get_create_url(cls):
        route = 'app:%s_create' % snake(cls.__name__)
        return reverse(route)

    def __str__(self):
        return self.name 


class AbstractModel(Base, models.Model):
    """
    Abstract model class, provides standard name and description fields, as
    well as methods return related objects. Subclasses will need to specify 
    foreign key fields.
    """

    def __init__(self, *args, **kwargs):
        super(AbstractModel, self).__init__(*args, **kwargs)

        # this is really hacky, for one reason, because it doesn't
        # set the new help_text until after the first time the
        # user sees it. leaving it for now though...

        verbose_name = self._meta.verbose_name
        help_text = 'Enter a name for this %s.' % verbose_name
        try:
            self._meta.get_field('name').help_text = help_text
        except Exception as e:
            logger.debug(e)

        help_text = 'Enter a description for this %s.' % verbose_name
        try:
            self._meta.get_field('description').help_text = help_text
        except Exception as e:
            logger.debug(e)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200, 
        help_text="Enter a name.", blank=True)

    description = models.TextField(max_length=1000, 
        help_text="Enter a description.", blank=True)

    # @property
    # def root(self):
    #     root_objects = set({})
    #     # import pdb; pdb.set_trace()
    #     parent_rels = self.get_parent_relations()
    #     for parent_rel in parent_rels:
    #         parent = parent_rel['object']
    #         if type(parent) == Parent:
    #             root_objects.add(parent)
    #         print parent, type(parent)

    class Meta:
        abstract = True


class Node(object):
    def __init__(self):
        self.name = ''
        self.left = []
        self.right = []
        self.obj = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'graph node: %s, |left| = %s, |right| = %s' % (
            self.name, str(len(self.left)), str(len(self.right)))


class InvestigationType(AbstractModel):
    """Model describing the types of projects that may be instantiated."""

    definition_file = models.FileField('definition file(s)', upload_to='documents/%Y/%m/%d/', 
        blank=True, null=True)

    def _build_graph(self, root):
        fk_type_rels = ['PART','ISIN','ISOU']
        temp_list = root.right
        for node in temp_list:
            for parent_rel in node.obj.forward_relationship_defs.filter(
                rel_type_abbr__in=fk_type_rels):
                parent = parent_rel.target
                parent_node = next(iter(
                    filter(lambda a,b=parent: a.obj==b, temp_list)))
                if not parent_node:
                    continue
                if parent_node not in node.left:
                    node.left.append(parent_node)
                if node not in parent_node.right:
                    parent_node.right.append(node)
                if node in root.right:
                    root.right.remove(node)
                if root in node.left:
                    node.left.remove(root)
    @property
    def bs_nested_list(self):
        y = ['Lungmap',
                ['My lungmap project',
                    ['specimen',
                        ['chunk',
                            ['process']],
                    'probe',
                        ['process'],
                    'process', 
                        ['image',
                            ['dataset']]]]]
        return y

    @property
    def graph(self):
        root = Node()
        root.name = 'Investigation Type: %s' % self.name
        root.obj = self

        for element_type in ElementType.objects.filter(investigation_type=self):
            n = Node()
            n.name = element_type.name
            n.left.append(root)
            root.right.append(n)
            n.obj = element_type

        self._build_graph(root)

        return root

    # def _build_dep_list(self, node):
    #     print node
    #     for child in node.right:
    #         self._build_dep_list(child)

    # @property
    # def dependency_list(self):
    #     return self._build_dep_list(self.graph)

    def save(self, *args, **kwargs):
        super(InvestigationType, self).save(*args, **kwargs)

        # TODO: move this code somewhere else, and don't run it in the django process!

        ElementType.objects.filter(investigation_type=self).delete()

        definitions = []
        try:
            definitions = [x for x in yaml.load_all(self.definition_file.file)]
        except Exception as e:
            logger.debug(e)
            return

        for definition in definitions:
            name = definition.get('name', '')

            description = definition.get('description', '')

            element_category = definition.get('element category', '') or \
                definition.get('category', '') or \
                definition.get('element type', '') or \
                definition.get('type', '')

            display_fields = definition.get('display fields', '') or \
                definition.get('display field', '')

            fields = definition.get('fields', [])

            elem_type = ElementType(
                name=name,
                description=description,
                investigation_type=self,
                element_category=element_category,
                display_fields=display_fields
            )

            elem_type.save()

            for field in fields:
                val_type = field.get('value type', '')
                value_type_abbr = ElementFieldDescriptor.CHAR

                try:
                    value_type_abbr = filter(
                        lambda x, y=val_type: x[1]==y, 
                        ElementFieldDescriptor.VALUE_TYPE_CHOICES
                    )[0][0]
                except Exception as e:
                    logger.debug(e)

                elem_field_descr = ElementFieldDescriptor(
                    label=field.get('name', ''),
                    help_text=field.get('description', ''),
                    value_type_abbr=value_type_abbr,
                    required=field.get('required', False),
                    element_type=elem_type,
                )

                elem_field_descr.save()

        for definition in definitions:
            rels = definition.get('rels', [])
        
            for rel in rels:
                card = rel.get('cardinality', '')
                card_abbr = RelationshipDefinition.ONE #default

                try:
                    card_abbr = filter(
                        lambda x, y=card: x[1]==y, 
                        RelationshipDefinition.CARDINALITIES)[0][0]
                except Exception as e:
                    logger.debug(e)

                rel_type = rel.get('type', '')
                rel_type_abbr = RelationshipDefinition.PART #default

                try:
                    rel_type_abbr = filter(
                        lambda x, y=rel_type: x[1]==y, 
                        RelationshipDefinition.RELATIONSHIP_TYPES)[0][0]
                except Exception as e:
                    logger.debug(e)

                source_name = definition.get('name', '')
                source = ElementType.objects.get(investigation_type=self, 
                    name__exact=source_name)
                target_name = rel.get('target', '')
                target = ElementType.objects.get(investigation_type=self, 
                    name__exact=target_name)

                rel_def = RelationshipDefinition(
                    source=source,
                    target=target,
                    rel_type_abbr=rel_type_abbr,
                    card_abbr=card_abbr
                )

                rel_def.save()

    class Meta:
        verbose_name = "investigation type"


class Project(AbstractModel):
    """Model representing an individual research project."""

    investigation_type = models.ForeignKey(InvestigationType, on_delete=models.CASCADE) 

    archive = models.FileField('bulk upload', upload_to='documents/%Y/%m/%d/', 
        blank=True, null=True)

    # TODO: add fk to owner/creator (auth.user)
    # TODO: add many-to-many to collaborators
        
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)

        # clear out anything that was previously created
        Element.objects.filter(project=self).delete()

        # TODO: create new investigation_type if user does not select existing
        if not self.investigation_type or not self.archive:
            return

        # TODO: handle zip of multiple csv, or just multiple csv uploads
        archive_file = self.archive.file
        if not archive_file.name.split('.')[-1] == 'csv':
            return
        
        reader = csv.DictReader(archive_file, 
            delimiter=str(u',').encode('utf-8'))

        rows = []
        # read entire csv into memory, could be prohibitive for huge sheets
        for row in reader:
            rows.append(row)

        # get list of elements for this investigation type
        element_types = ElementType.objects.filter(
            investigation_type=self.investigation_type)

        # we're going to stick values in here the first time we see them
        # if values are not unique, we do not create a new element
        unique_element_strings = set()

        # the following seems fairly inefficient, but it works to create 
        # unique elements (relationships between elements are established
        # in a subsequent step).
        # - loop though each element type definition
        # - for each element type, loop through each row of csv
        # - for each row, loop through each (element type) field
        # - get the field value from the csv and add to a dictionary
        # - use complete list of k,v pairs to create a new element string
        # - if element string found in set of unique values continue, else
        # - save element to db and store string in unique set  
        for element_type in element_types:

            pk_id = None

            # get field defs for this element type
            field_descriptors = element_type.elementfielddescriptor_set.all()

            # loop through all rows in the csv
            for row in rows:

                # temporarily hold field values
                field_values = {}
                descriptor_values = []

                # grab all field values for this element in this row
                for field_descriptor in field_descriptors:
                    field_name = field_descriptor.label
                    field_value = row.get(field_name).lstrip().rstrip()
                    if field_value:
                        # use this to check for uniqueness
                        field_values.update({field_name: field_value})
                        # use this to create a new field_value if unique
                        descriptor_values.append([
                            field_descriptor.value_type, 
                            field_value,
                            field_descriptor,
                        ])

                # we need a hashable object to check for uniqueness
                value_string = str(field_values)

                # check for uniqueness
                if not value_string in unique_element_strings:

                    # if new element, create a new unique id
                    pk_id = uuid.uuid4()

                    # do all the commits together
                    with transaction.atomic():
                        # create a new element
                        new_element = Element(id=pk_id,
                            element_type=element_type, project=self)
                        new_element.save()

                        # create the new field values
                        for value_type, value, descriptor in descriptor_values:
                            field_value = value_type(
                                value=value,
                                element_field_descriptor=descriptor,
                                element=new_element
                            )
                            field_value.save()

                        # add value string to set
                        unique_element_strings.add(value_string)

                #row.update({'__%s__' % element_type.name : 
                #    [pk_id, element_type, descriptor_values]})
                row.update({'__%s__ID' % element_type.name : pk_id})

        #######################
        ## add relationships ##
        #######################

        # do all the commits together
        with transaction.atomic():

            # loop through each row from csv file (now containing uuids)
            for row in rows:

                # loop through all our element types
                for element_type in element_types:

                    # get uuid for element_type's element in this row
                    pk_id = row.get('__%s__ID' % element_type.name)

                    # loop through 'has input', 'has output', etc. type rels
                    for rel_def in element_type.from_relationships:

                        card = rel_def.card_abbr
                        target_type = rel_def.target
                        fk_id = row.get('__%s__ID' % target_type.name)

                        if pk_id and fk_id:
                            if card in ['ONE','ZO']:

                                # any existing rels between these elements?
                                rels = Relationship.objects.filter(
                                    source_id=pk_id, 
                                    target__element_type=target_type
                                )

                                # if relationship already exists...
                                if rels:

                                    # create a duplicate element to point to
                                    element = Element.objects.get(pk=pk_id)
                                    element.id = None
                                    element.save()

                                    # update the element_type's element id in
                                    # the row

                                    pk_id = element.id
                                    row['__%s__ID' % element_type.name] = pk_id

                                    rels = Relationship.objects.filter(
                                        source_id=pk_id, 
                                        target_id=fk_id,
                                    )

                            # create new relationship
                            rel = Relationship(
                                source_id=pk_id, 
                                target_id=fk_id,
                                relationship_definition=rel_def)
                            rel.save()


class ElementType(AbstractModel):
    """Model describing the types of entities that may be instantiated 
    per investigation type."""

    investigation_type = models.ForeignKey(InvestigationType, on_delete=models.CASCADE) 

    MAT = 'M'
    DAT = 'D'
    PRO = 'P'

    ELEMENT_CATEGORIES = (
        (MAT, 'material'),
        (DAT, 'data'),
        (PRO, 'process'),
    )

    element_category = models.CharField(
        'element category',
        max_length = 1,
        choices = ELEMENT_CATEGORIES,
        default=MAT,
        help_text="Which category is this element type? Material, data, or process?"
    )

    display_fields = models.CharField(max_length=200, 
        help_text="List the fields that should be used to label elements of this type in a list", blank=True)

    @property
    def verbose_element_category(self):
        try:
            return filter(lambda x, y=self.element_category: x[0]==y, 
                self.ELEMENT_CATEGORIES)[0][1]
        except Exception as e:
            logger.debug(e)

        # falls through to here if not found
        return self.element_category

    @property
    def display_field_list(self):
        return self.display_fields.split(',')

    @property
    def to_relationships(self):
        return self.forward_relationship_defs.filter(
            rel_type_abbr__in=['PART','ISIN','ISOU'])

    @property
    def from_relationships(self):
        return self.forward_relationship_defs.filter(
            rel_type_abbr__in=['CONT','ORIG','HASI','HASO'])

    def save(self, *args, **kwargs):
        self.display_fields = ','.join(filter(lambda x: x is not '', 
            [x.rstrip().lstrip() for x in self.display_fields.split(',')]))

        if self.element_category:
            first_letter = self.element_category[0]
            if first_letter.lower() == 'd':
                self.element_category = self.DAT
            elif first_letter.lower() == 'p':
                self.element_category = self.PRO
            else:
                self.element_category = self.MAT

        super(ElementType, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "element type"


class ElementFieldDescriptor(Base, models.Model):
    """Model describes an attribute of an element."""

    #############
    # Attributes
    #############

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    label = models.CharField(max_length=200, 
        help_text="Enter a label for this field.", blank=True)

    help_text = models.TextField(max_length=1000, 
        help_text="Enter help text for this field.",
        blank=True)

    CHAR = 'CHR'
    TEXT = 'TXT'
    INT = 'INT'
    FLOAT = 'FLT'
    DATE = 'MDY'
    URL = 'URL'
    REL = 'REL'
    VALUE_TYPE_CHOICES = (
        (CHAR, 'short text'),
        (TEXT, 'long text'),
        (INT, 'integer'),
        (FLOAT, 'real number'),
        (DATE, 'date'),
        (URL, 'url'),
        (REL, 'relation'),
    )

    value_type_abbr = models.CharField(
        "value type",
        max_length=3,
        choices=VALUE_TYPE_CHOICES,
        default=CHAR,
    )

    required = models.BooleanField(default=False, 
        help_text="Is this a required field?")

    ###############
    # Foreign Keys
    ###############

    element_type = models.ForeignKey(ElementType, on_delete=models.CASCADE) 

    #############
    # Properties    
    #############

    @property
    def value_type_map(self):
        mapping = {                                                        
            self.CHAR: ElementCharFieldValue,
            self.TEXT: ElementTextFieldValue,
            self.INT: ElementIntFieldValue,
            self.FLOAT: ElementFloatFieldValue,
            self.DATE: ElementDateFieldValue,
            self.URL: ElementUrlFieldValue,
            self.REL: ElementCharFieldValue, # TODO: add rel field 
        } 
        return mapping

    @property
    def value_type(self):
        return self.value_type_map[self.value_type_abbr]

    @property
    def verbose_value_type(self):
        try:
            return filter(lambda x, y=self.value_type_abbr: x[0]==y,self.VALUE_TYPE_CHOICES)[0][1]
        except Exception as e:
            logger.debug(e)

        return self.value_type_abbr

    ##########
    # Methods
    ##########

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "element field descriptor"


class RelationshipDefinition(Base, models.Model):
    """Describes a the relationships that may exist between element types."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(ElementType, on_delete=models.CASCADE, 
        related_name='forward_relationship_defs')
    target = models.ForeignKey(ElementType, on_delete=models.CASCADE, 
        related_name='reverse_relationship_defs')
    
    ORIG = 'ORIG'
    PART = 'PART'
    ISIN = 'ISIN'
    ISOU = 'ISOU'
    HASI = 'HASI'
    HASO = 'HASO'
    CONT = 'CONT'

    RELATIONSHIP_TYPES = (
        (ORIG, 'is origin of'),
        (PART, 'is part of'),
        (ISIN, 'is input to'),
        (ISOU, 'is output of'),
        (HASI, 'has input'),
        (HASO, 'has output'),
        (CONT, 'contains'),
    )

    rel_type_abbr = models.CharField(
        "relationship type",
        max_length = 4,
        choices = RELATIONSHIP_TYPES,
        default=PART,
    )

    ONE = 'ONE'
    ZO = 'ZO'
    MANY = 'MANY'
    OM = 'OM'
    ZOM = 'ZOM'

    CARDINALITIES = (
        (ONE, 'one'),
        (ZO, 'zero or one'),
        (MANY, 'many'),
        (OM, 'one or many'),
        (ZOM, 'zero one or many'),
    )

    card_abbr = models.CharField(
        'cardinality',
        max_length = 4,
        choices = CARDINALITIES,
        default=ONE,
    )

    @property
    def verbose_relationship_type(self):
        try:
            return filter(lambda x, y=self.rel_type_abbr: x[0]==y, 
                self.RELATIONSHIP_TYPES)[0][1]
        except Exception as e:
            logger.debug(e)

        return self.rel_type_abbr

    @property
    def verbose_cardinality(self):
        try:
            return filter(lambda x, y=self.card_abbr: x[0]==y, 
                self.CARDINALITIES)[0][1]
        except Exception as e:
            logger.debug(e)

        return self.card_abbr

    def __str__(self):
        return '%s %s %s %s' % (
            self.source.name, 
            self.verbose_relationship_type, 
            self.verbose_cardinality,
            self.target.name
        )


class Path(models.Model):
    """
    Collection of all elements with some immediate or distant
    relationship to another element or dataset.
    """
    # TODO: Do we need to inherit from base?
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class PathMember(Base, models.Model):
    """Provides a link from an element to a path."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.ForeignKey(Path, on_delete=models.CASCADE, editable=False)
    element = models.ForeignKey('Element', on_delete=models.CASCADE)


class Checksum(Base, models.Model):
    """Relates two elements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: should i change this to a field? like url, maybe sra?
    data = models.ForeignKey('Element', on_delete=models.CASCADE)

    REQ = 'REQ'
    ERR = 'ERR'
    CMP = 'CMP' 

    STATUS_TYPES = (
        (REQ, 'requested'),
        (ERR, 'failed'),
        (CMP, 'completed'),
    )

    status = models.CharField(
        "status",
        max_length = 3,
        choices = STATUS_TYPES,
        default=REQ,
    )

    WEB = 'WEB'
    SRA = 'SRA'
    AGV = 'AGV' 

    RESOURCE_TYPES = (
        (WEB, 'url'),
        (SRA, 'sra'),
        (AGV, 'agave'),
    )

    resource_type = models.CharField(
        "resource type",
        max_length = 3,
        choices = RESOURCE_TYPES,
        default=WEB,
    )

    jobid = models.CharField(max_length=40, 
        help_text="Checksum job id",blank=True)
    value = models.CharField(max_length=200, 
        help_text="Checksum value",blank=True)
    error_message = models.CharField(max_length=512, 
        help_text="Error message",blank=True)
    initiated = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # TODO set completed date when value is set
        if self.id:
            if not self.completed:
                self.completed = timezone.now()
        return super(Checksum, self).save(*args, **kwargs)

    def __str__(self):
        s = ''
        if self.status == self.ERR:
            s = 'checksum failed at: %s (%s)' % (
                str(self.completed), self.error_message)
        elif self.status == self.CMP:
            s = 'checksum completed at: %s (%s)' % (
                str(self.completed), self.value)
        else:
            s = 'checksum requested at: %s' % str(self.initiated)
        return s


class Element(AbstractModel):
    """Model representing an individual element."""

    element_type = models.ForeignKey(ElementType, on_delete=models.CASCADE) 
    project = models.ForeignKey(Project, on_delete=models.CASCADE) 
    path = models.OneToOneField(Path, on_delete=models.CASCADE, 
        null=True, blank=True)

    @property
    def element_category(self):
        return self.element_type.element_category

    def _set_display_name(self):
        display_items = []
        display_fields = self.element_type.display_field_list
        with transaction.atomic():
            for display_field in display_fields:
                # doing a filter here in case there are multiple fields with
                # the same label, but who would do that
                descriptors = self.element_type.elementfielddescriptor_set.filter(
                    label=display_field)
                # get the first descriptor if there are many
                descriptor = next(iter(descriptors), None)
                if descriptor:
                    # get the type of value, for instance, char, text, date
                    value_type = descriptor.value_type
                    if value_type:
                        # query for values that are linked to this element,
                        # and the field descriptor from above
                        field_values = value_type.objects.filter(element=self, 
                            element_field_descriptor=descriptor)
                        # get the first one, we should have at most one anyway
                        field_value = next(iter(field_values), None)
                        if field_value:
                            display_items.append('%s: %s' % (descriptor.label,
                                field_value.value))

                # the downside of doing this below instead of the mess above:
                # the name field will not get populated if you happen to 
                # have multiple descriptors to the same element type to the
                # same field TODO: make sure can't have duplicate descriptors

                # try:
                #     descriptor = \
                #         self.element_type.elementfielddescriptor_set.get(
                #             label=display_field
                #        )
                #    field_values = \
                #        descriptor.value_type.objects.get(
                #            element=self, 
                #            element_field_descriptor=descriptor
                #        )
                #    display_items.append('%s: %s' % (
                #            descriptor.label,
                #            field_value.value
                #        )
                #    )
                # except Exception as e:
                #     logger.debug(e)
                #     return

            self.name = '%s: %s' % (self.element_type.name.title(),
                ','.join(display_items))
            self.save()

    def initiate_checksum(self):
        if not self.id:
            logger.error('Checksum attempted on unsaved data element.')
            return

        # this is super hacky, i'd like to just mark fields in the
        # yaml as containing the location to checksum, and then
        # checksum would be associated directly with the field values
        url = next(iter(
                [field.value for field in self.elementurlfieldvalue_set.all()]
            ),None)
        path = next(iter(
                [field.value for field in self.elementcharfieldvalue_set.all()\
                    if 'path' in field.element_field_descriptor.label.lower() \
                    and 'agave://' in field.value]
            ),None)
        sra = next(iter(
                [field.value for field in self.elementcharfieldvalue_set.all()\
            if 'sra' in field.element_field_descriptor.label.lower()]),None)

        inputs = {}
        parameters = {}
        resource_type = None
        if url:
            parameters.update({'URL': url})
            resource_type = 'WEB'
        elif sra:
            parameters.update({'SRA': sra})
            resource_type = 'SRA'
        elif path:
            inputs.update({'AGAVE_URL': path})
            resource_type = 'AGV'
        else:
            logger.debug(
                'Could not initiate checksum, no location information found.')
            return

        checksum = Checksum(data=self, resource_type=resource_type)

        parameters.update({'UUID': str(checksum.id)})

        body = {
            'name': 'checksum',
            'appId': 'idsvc_checksum-0.1',
            'inputs': inputs,
            'parameters': parameters,
            'archive': True,
            'archivePath': 'idsvc_user/archive/jobs/${JOB_NAME}=${JOB_ID}'
        }

        try:
            response = portal_agave_client.jobs.submit(body=body)
            checksum.jobid = response['id']
            checksum.save()
            logger.debug(
                'Checksum job id: %s' % response['id']
            )
        except Exception as e:
            error_msg = 'Checksum job was not successfully initated.'
            logger.error('%s -- %s' % (error_msg, e))

    def save(self, *args, **kwargs):
        # make sure each dataset has a path
        path, created = Path.objects.get_or_create(element=self)
        if created:
            self.path = path

        super(Element, self).save(*args, **kwargs)

        if self.element_category == ElementType.DAT:
            #TODO trigger checksum app
            # self.initiate_checksum()
            pass

    def __str__(self):
        if self.name == '':
            self._set_display_name()
        return self.name


class Relationship(Base, models.Model):
    """Relates two elements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(Element, on_delete=models.CASCADE, 
        related_name='incoming_relationships')

    target = models.ForeignKey(Element, on_delete=models.CASCADE, 
        related_name='outgoing_relationships')

    relationship_definition = models.ForeignKey(RelationshipDefinition, 
        on_delete=models.CASCADE, related_name='definition')

    def __str__(self):
        return '%s - %s' % (self.source.name, self.target.name)


class DatasetLink(Base, models.Model):
    """Relates two elements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE)
    datum = models.ForeignKey(Element, on_delete=models.CASCADE)

    def __str__(self):
        return 'Dataset %s contains %s' % (self.dataset.name, self.datum.name)


class Dataset(AbstractModel):
    """Joins data elements in one grouping through value query"""
    # TODO: get rid of name and description?

    project = models.ForeignKey(Project, on_delete=models.CASCADE) 

    query = models.TextField(blank=True, null=True, 
        help_text='element type.field name = value')

    status = models.CharField(max_length=200, blank=True, null=True,
        default='', editable=False)

    path = models.OneToOneField(Path, on_delete=models.CASCADE,
        null=True, blank=True, editable=False)

    def request_doi(self):
        logger.debug('requesting doi')
        pass

    def save(self, *args, **kwargs):
        path, created = Path.objects.get_or_create(dataset=self)

        if created:
            self.path = path

        # remove any previously existing path members
        PathMember.objects.filter(path=self.path).delete()

        # delete any previous links to this dataset
        DatasetLink.objects.filter(dataset=self).delete()

        # make query string uniform and replace space with white space
        # with characters that makes it easier to split off the boolean
        # and equlity operators
        query = self.query\
            .replace('==','=').replace('!=','#').replace('<>','#')\
            .replace(' = ','=').replace(' # ','#')\
            .replace(' IN ','^').replace(' in ','^')\
            .replace('(','').replace(')','')\
            .replace('=','(=)').replace('#','(#)').replace('^','(^)')\
            .replace('&&','AND').replace('||','OR')\
            .replace('&','AND').replace('|','OR')\
            .replace(' and ', ' AND ').replace(' or ', ' OR ')\
            .replace('<','').replace('>','')\
            .replace(' AND ', '<AND>').replace(' OR ', '<OR>')\

        # symbols that we will use to split the string
        symbols = ['>','<',')','(','.']

        is_value = False

        # split query into all the parts
        query_parts = [query]
        for symbol in symbols:
            temp_parts = []
            for part in query_parts:
                # problem, we don't want to split decimal values
                # i should fix this with reg exp, but i'm not going to
                # so i'm going to check to see if the last part was
                # an equality operator
                if is_value:
                    temp_parts.append(part)
                else:
                    temp_parts.extend(part.split(symbol))
                is_value = part in ['=','#','^']
            query_parts = temp_parts

        # get rid of any extra whitespace
        query_parts = map(lambda x: x.rstrip().lstrip(), query_parts)

        # we'll use a named tuple to store the parts for each selection
        Term = namedtuple('Term', ['table','field','operator','value'])
        
        terms = []
        set_operators = []

        # create lists of terms and boolean operators
        while len(query_parts) >= 4:
            terms.append(Term(*query_parts[:4]))
            query_parts = query_parts[4:]
            if query_parts:
                set_operators.append(query_parts[0])
                query_parts = query_parts[1:]

        bag = []
        # do query for each term
        for term in terms:
            element_type_name = term.table
            field_name = term.field
            value = term.value
            equality_operator = term.operator

            standard_field = field_name.lower() in ['id','name']

            if standard_field:
                # if equality operator is: equal
                if equality_operator == '=':
                    values = Element.objects.filter(
                        project=self.project, **{field_name:value})

                # if equality operator is: not equal
                elif equality_operator == '#':
                    values = Element.objects.filter( 
                        project=self.project).exclude(
                            **{field_name:value})

                # if equality operator is: in
                elif equality_operator == '^':
                    values = Element.objects.filter(
                        project=self.project, **{field_name:value})

            else:
                # get the descriptor for this field on this element_type
                # (we're going to take the first one because why would you have
                # the same field twice on one element? you might though so that's
                # why i'm using filter rather than get)
                descriptors = ElementFieldDescriptor.objects.filter(
                    element_type__name=element_type_name,
                    label=field_name
                )
                descriptor = next(iter(descriptors), None)
                if not descriptor:
                    self.status = 'element or field not found'
                    super(Dataset, self).save(*args, **kwargs)
                    return

                # query this project's value_types (e.g. ElementCharFieldValue)
                # for the given value
                value_type = descriptor.value_type

                # if equality operator is: equal
                if equality_operator == '=':
                    values = value_type.objects.filter(value=value, 
                        element_field_descriptor=descriptor, 
                        element__project=self.project)

                # if equality operator is: not equal
                elif equality_operator == '#':
                    values = value_type.objects.filter( 
                        element_field_descriptor=descriptor, 
                        element__project=self.project).exclude(value=value)

                # if equality operator is: in
                elif equality_operator == '^':
                    values = value_type.objects.filter(value__in=value,
                        element_field_descriptor=descriptor, 
                        element__project=self.project)

                else:
                    self.status = 'query syntax error'
                    super(Dataset, self).save(*args, **kwargs)
                    return

            if not values:
                self.status = 'value not found.'
                super(Dataset, self).save(*args, **kwargs)
                return

            # grab the elements from the queried field values
            # put the elements in a queue (a set, we want only unique elements)
            if standard_field:
                element_queue = set(values)
            else:
                element_queue = set([x.element for x in values])
            visited = set()
            self.status = '%s elements found' % len(element_queue)

            data = set()

            # while the queue is not empty
            while element_queue:

                # pop an element off
                element = element_queue.pop()
                # and add it to the set of element which we've already seen
                visited.add(element)

                # if the element is a data type, add to our list of data
                if element.element_type.element_category == 'D':
                    data.add(element)

                # else if it is a process type, add it's output to the queue
                elif element.element_type.element_category == 'P':
                    unvisited = set([x.target for x in \
                        element.incoming_relationships.filter(
                            relationship_definition__rel_type_abbr__in=\
                            ['HASO']) \
                        if x not in visited and \
                        x not in data])
                    element_queue.update(unvisited)

                # else if it is a material entity, find elements to which
                # it is input, or elements that originated from it, and
                # add them to the queue
                else:
                    unvisited = set([x.source for x in \
                        element.outgoing_relationships.filter(
                            relationship_definition__rel_type_abbr__in=['HASI']) \
                        if x not in visited and \
                        x not in data])
                    element_queue.update(unvisited)

                    unvisited = set([x.target for x in \
                        element.incoming_relationships.filter(
                            relationship_definition__rel_type_abbr__in=\
                            ['CONT','ORIG']) \
                        if x not in visited and \
                        x not in data])
                    element_queue.update(unvisited)

            bag.append(data)

        if bag:
            ds = set(bag.pop())
        else:
            self.status = '0 data elements found, likely bad query'
            super(Dataset, self).save(*args, **kwargs)
            return

        # combine results
        for set_operator in set_operators:
            if set_operator == 'AND':
                ds = ds.intersection(bag.pop())
            elif set_operator == 'OR':
                ds = ds.union(bag.pop())

        # this is not super fancy, little status message with the number
        # of data elements we found
        self.status = 'registered %s data elements' % len(ds)

        # save the links
        with transaction.atomic():
            for datum in ds:
                if not DatasetLink.objects.filter(dataset=self, datum=datum):
                    rel = DatasetLink(dataset=self, datum=datum)
                    rel.save()

        # save the dataset
        super(Dataset, self).save(*args, **kwargs)

        ## add elements to path ##

        # add contents of dataset to a queue
        path_queue = set(ds)
        # clear visisted set
        visited.clear()

        path_members = set()

        ### hurts my brain

        # so we start with the data elements (images in james's case)
        # the images are contained by this dataset
        # connected by a DatasetLink: Dataset<-DatasetLink->Data
        # for each image we want to know what process created it
        # and we want to know the inputs to those processes
        # and we want to know the 'parents' of those inputs

        # the image has a fk to the process
        # from the image perspective, the process is a...
        # 

        ###


        # while the queue is not empty
        while path_queue:
            # pop an element off
            element = path_queue.pop()
            # and add it to the set of element which we've already seen
            visited.add(element)
            ###
            if element in path_members:
                continue

            if element.element_type.element_category == 'D':
                if element in ds:
                    path_members.add(element)
            elif element.element_type.element_category == 'P':
                path_members.add(element)
            else:
                path_members.add(element)

            unvisited = set([x.source for x in \
                element.outgoing_relationships.all()
                if x not in visited and \
                x not in path_members])
            path_queue.update(unvisited)

            print "\nincoming unvisited: %s\n" % (unvisited)
            print element.incoming_relationships.all()

            unvisited = set([x.target for x in \
                element.incoming_relationships.all()
                if x not in visited and \
                x not in path_members])
            path_queue.update(unvisited)

            print "\noutgoing unvisited: %s\n" % (unvisited)
            print element.outgoing_relationships.all()

            # # if the element is a data type, add to our list of data
            # if element.element_type.element_category == 'D':
            #     unvisited = set([x.target for x in \
            #         element.outgoing_relationships.filter(
            #             relationship_definition__rel_type_abbr__in=\
            #             ['HASI']) \
            #         if x not in visited and \
            #         x not in path_members])
            #     path_queue.update(unvisited)
            # 
            #     print unvisited
            #
            # # else if it is a process type, add it's output to the queue
            # elif element.element_type.element_category == 'P':
            #     unvisited = set([x.target for x in \
            #         element.incoming_relationships.filter(
            #             relationship_definition__rel_type_abbr__in=\
            #             ['HASI']) \
            #         if x not in visited and \
            #         x not in path_members])
            #     path_queue.update(unvisited)
            # 
            # # else if it is a material entity, find elements to which
            # # it is input, or elements that originated from it, and
            # # add them to the queue
            # else:
            #     unvisited = set([x.source for x in \
            #         element.outgoing_relationships.filter(
            #             relationship_definition__rel_type_abbr__in=['PART']) \
            #         if x not in visited and \
            #         x not in path_members])
            #     path_queue_queue.update(unvisited)
            # 
                # unvisited = set([x.target for x in \
                #     element.incoming_relationships.filter(
                #         relationship_definition__rel_type_abbr__in=\
                #         ['CONT','ORIG']) \
                #     if x not in visited and \
                #     x not in path_members])
                # path_queue.update(unvisited)

        for element in path_members:
            PathMember.objects.create(path=self.path, element=element)

    def __str__(self):
        if not self.name == '':
            return self.name
        else:
            return self.query


class AbstractElementFieldValue(Base, models.Model):
    """Abstract class for various types of element field values"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ###############
    # Foreign Keys
    ###############

    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    element_field_descriptor = models.ForeignKey(ElementFieldDescriptor, 
        on_delete=models.CASCADE, null=True)

    ##########
    # Methods
    ##########

    def save(self, *args, **kwargs):
        super(AbstractElementFieldValue, self).save(*args, **kwargs)
        field_name = self.element_field_descriptor.label
        if field_name in self.element.element_type.display_field_list:
            self.element._set_display_name()

    def __str__(self):
        return str(self.value)

    #######
    # Meta
    #######

    class Meta:
        abstract = True


class ElementCharFieldValue(AbstractElementFieldValue):
    """Element char field attribute value."""

    value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = 'short text value'


class ElementTextFieldValue(AbstractElementFieldValue):
    """Element text field attribute value."""

    value = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'long text value'


class ElementIntFieldValue(AbstractElementFieldValue):
    """Element CharField attribute value."""

    value = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'integer value'


class ElementFloatFieldValue(AbstractElementFieldValue):
    """Element CharField attribute value."""

    value = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = 'float value'


class ElementDateFieldValue(AbstractElementFieldValue):
    """Element date field attribute value."""

    value = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    class Meta:
        verbose_name = 'date value'


class ElementUrlFieldValue(AbstractElementFieldValue):
    """Element CharField attribute value."""

    value = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'url value'


# class ElementRelFieldValue(AbstractElementFieldValue):
#     """Element CharField attribute value."""
# 
#     value = models.CharField(max_length=200, blank=True, null=True)
# 
#     class Meta:
#         verbose_name = 'url'
