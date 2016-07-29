import json
import logging

logger = logging.getLogger(__name__)


class MetadataRelationshipMixin(object):
    """Mixin with BaseMetadata"""

    parent_relationship_types = ('HasPart', 'HasDerivative', 'HasInput', 'HasOutput')
    child_relationship_types = ('IsPartOf', 'IsDerivedFrom', 'IsInputTo', 'IsOutputOf')

    def _get_related_objects_by_type(self, rel_type):
        """Helper method, returns objects related to this object with specific relationship type"""
        if rel_type not in self.parent_relationship_types + self.child_relationship_types:
            raise Exception('Invalid relationship type.')

        related = []
        for related_object in self.related_objects:
            for relationship in related_object.value.get('_relationships', []):
                if relationship['@id'] == self.uuid and relationship['@rel:type'] == rel_type:
                    related.append(related_object)

        return related

    #########
    # PARTS #
    #########

    @property
    def parts(self):
        """
        Get all objects that are part of this object.

        Relationship:

            This Object: HasPart: Related Object
            Related Object: IsPartOf: This Object

        Returns List
        """
        return self._get_related_objects_by_type('IsPartOf')

    def add_part(self, part_object):
        """
        Add an objects that is part of this object.

        Relationship:

            This Object: HasPart: Related Object
            Related Object: IsPartOf: This Object

        Returns None
        """
        if 'uuid' not in dir(part_object) or not part_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasPart',
            '@id': part_object.uuid
        }

        self.add_relationship(relationship)

    def remove_part(self, part_object):
        """
        Remove relationship to an object that is part of this object.

        Relationship:

            This Object: HasPart: Related Object
            Related Object: IsPartOf: This Object

        Returns None
        """
        if 'uuid' not in dir(part_object) or not part_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasPart',
            '@id': part_object.uuid
        }

        self.remove_relationship(relationship)

    ##############
    # CONTAINERS #
    ##############

    @property
    def containers(self):
        """
        Get all objects that contain this object.

        Relationship:

            This Object: IsPartOf: Related Object
            Related Object: HasPart: This Object

        Returns List
        """
        # Query related objects that have HasPart type relationships to this object.
        return self._get_related_objects_by_type('HasPart')

    def add_container(self, container_object):
        """
        Add an object that contains this object.

        Relationship:

            This Object: IsPartOf: Related Object
            Related Object: HasPart: This Object

        Returns None
        """
        if 'uuid' not in dir(container_object) or not container_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsPartOf',
            '@id': container_object.uuid
        }

        self.add_relationship(relationship)

    def remove_container(self, container_object):
        """
        Remove relationship to an object that contains this object.

        Relationship:

            This Object: IsPartOf: Related Object
            Related Object: HasPart: This Object

        Returns None
        """
        if 'uuid' not in dir(container_object) or not container_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsPartOf',
            '@id': container_object.uuid
        }

        self.remove_relationship(relationship)

    ###############
    # DERIVATIVES #
    ###############

    @property
    def derivatives(self):
        """
        Get all objects derived from this objects.

        Relationship:

            This Object: HasDerivative: Related Object
            Related Object: IsDerivedFrom: This Object

        Returns List
        """
        # Query related objects that have IsDerivedFrom type relationships to this object.
        return self._get_related_objects_by_type('IsDerivedFrom')

    def add_derivative(self, derived_object):
        """
        Add an object that is derived from this objects.

        Relationship:

            This Object: HasDerivative: Related Object
            Related Object: IsDerivedFrom: This Object

        Returns None
        """
        if 'uuid' not in dir(derived_object) or not derived_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasDerivative',
            '@id': derived_object.uuid
        }

        self.add_relationship(relationship)

    def remove_derivative(self, derived_object):
        """
        Remove relationship to an object that is derived from this objects.

        Relationship:

            This Object: HasDerivative: Related Object
            Related Object: IsDerivedFrom: This Object

        Returns None
        """
        if 'uuid' not in dir(derived_object) or not derived_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasDerivative',
            '@id': derived_object.uuid
        }

        self.remove_relationship(relationship)

    ##############
    # PRECURSORS #
    ##############

    # TODO: this should probably be source, not precursor

    @property
    def precursors(self):
        """
        Get object(s) from which this object is derived.

        Relationship:

            This Object: IsDerivedFrom: Related Object
            Related Object: HasDerivative: This Object

        Returns List
        """
        # Query related objects that have HasDerivative type relationships to this object.
        return self._get_related_objects_by_type('HasDerivative')

    def add_precursor(self, precursor_object):
        """
        Add an object from which this object is derived.

        Relationship:

            This Object: IsDerivedFrom: Related Object
            Related Object: HasDerivative: This Object

        Returns None
        """
        if 'uuid' not in dir(precursor_object) or not precursor_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsDerivedFrom',
            '@id': precursor_object.uuid
        }

        self.add_relationship(relationship)

    def remove_precursor(self, precursor_object):
        """
        Remove relationship to an object from which this object is derived.

        Relationship:

            This Object: IsDerivedFrom: Related Object
            Related Object: HasDerivative: This Object

        Returns None
        """
        if 'uuid' not in dir(precursor_object) or not precursor_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsDerivedFrom',
            '@id': precursor_object.uuid
        }

        self.remove_relationship(relationship)

    ##########
    # Inputs #
    ##########

    @property
    def inputs(self):
        """
        Get all inputs belonging to this objects.

        Relationship:

            This Object: HasInput: Related Object
            Related Object: IsInputTo: This Object

        Returns List
        """
        # Query related objects that have IsInputTo type relationships to this object.

        return self._get_related_objects_by_type('IsInputTo')

    def add_input(self, my_input):
        """
        Add input for this object.

        Relationship:

            This Object: HasInput: Related Object
            Related Object: IsInputTo: This Object

        Returns None
        """
        if 'uuid' not in dir(my_input) or not my_input.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasInput',
            '@id': my_input.uuid
        }

        self.add_relationship(relationship)

    def remove_input(self, my_input):
        """
        Remove input from this objects.

        Relationship:

            This Object: HasInput: Related Object
            Related Object: IsInputTo: This Object

        Returns None
        """
        if 'uuid' not in dir(my_input) or not my_input.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasInput',
            '@id': my_input.uuid
        }

        self.remove_relationship(relationship)

    ###########
    # Outputs #
    ###########

    @property
    def outputs(self):
        """
        Get all outputs from this objects.

        Relationship:

            This Object: HasOutput: Related Object
            Related Object: IsOutputOf: This Object

        Returns List
        """
        # Query related objects that have IsOutputOf type relationships to this object.
        return self._get_related_objects_by_type('IsOutputOf')

    def add_output(self, my_output):
        """
        Add output for this object.

        Relationship:

            This Object: HasOutput: Related Object
            Related Object: IsOutputOf: This Object

        Returns None
        """
        if 'uuid' not in dir(my_output) or not my_output.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasOutput',
            '@id': my_output.uuid
        }

        self.add_relationship(relationship)

    def remove_outputs(self, my_output):
        """
        Remove output from this objects.

        Relationship:

            This Object: HasOutput: Related Object
            Related Object: IsOutputOf: This Object

        Returns None
        """
        if 'uuid' not in dir(my_output) or not my_output.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasOutput',
            '@id': my_output.uuid
        }

        self.remove_relationship(relationship)

    #############
    # IsInputTo #
    #############

    @property
    def is_input_to(self):
        """
        Get object for which this object is unput.

        Relationship:

            This Object: IsInputTo: Related Object
            Related Object: HasInput: This Object

        Returns List
        """
        # Query related objects that have IsInputTo type relationships to this object.
        return self._get_related_objects_by_type('HasInput')

    def add_is_input_to(self, related_object):
        """
        Add input for this object.

        Relationship:

            This Object: IsInputTo: Related Object
            Related Object: HasInput: This Object

        Returns None
        """
        if 'uuid' not in dir(related_object) or not related_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsInputTo',
            '@id': related_object.uuid
        }

        self.add_relationship(relationship)

    def remove_is_input_to(self, related_object):
        """
        Remove input from this objects.

        Relationship:

            This Object: IsInputTo: Related Object
            Related Object: HasInput: This Object

        Returns None
        """
        if 'uuid' not in dir(related_object) or not related_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsInputTo',
            '@id': related_object.uuid
        }

        self.remove_relationship(relationship)

    ##############
    # IsOutputOf #
    ##############

    @property
    def is_output_of(self):
        """
        Get object for which this object is output.

        Relationship:

            This Object: IsOutputOf: Related Object
            Related Object: HasOutput: This Object

        Returns List
        """
        # Query related objects that have IsOutputOf type relationships to this object.
        return self._get_related_objects_by_type('HasOutput')

    def add_is_output_of(self, related_object):
        """
        Add output for this object.

        Relationship:

            This Object: HasOutput: Related Object
            Related Object: IsOutputOf: This Object

        Returns None
        """
        if 'uuid' not in dir(related_object) or not related_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsOutputOf',
            '@id': related_object.uuid
        }

        self.add_relationship(relationship)

    def remove_is_input_of(self, related_object):
        """
        Remove output from this objects.

        Relationship:

            This Object: HasOutput: Related Object
            Related Object: IsOutputOf: This Object

        Returns None
        """
        if 'uuid' not in dir(related_object) or not related_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'IsOutputOf',
            '@id': related_object.uuid
        }

        self.remove_relationship(relationship)

    #################
    # RELATIONSHIPS #
    #################

    def _get_related_meta(self):
        """Internal method, queries agave tenant for all related objects, returns list."""
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # get all objects with relationship to this object.
        query = {'value._relationships': {'$elemMatch': {'@id': self.uuid}}}
        relationships = self._api_client.meta.listMetadata(q=json.dumps(query))

        return relationships

    def _get_related_objects(self):
        """Instantiates all related meta into IDS model objects."""

        related_objects = []

        for related_meta in self._get_related_meta():
            try:
                # instantiate related objects
                related_object = self.get_class_by_name(related_meta.name)(
                    meta=related_meta,
                    api_client=self._api_client
                )

                # append to list
                related_objects.append(related_object)
            except Exception as e:
                logger.exception(e)

        return related_objects

    @property
    def relationships(self):
        """
        List relationships to this object, in the form:
            {
                '@rel:type': [HasPart|IsPartOf|HasDerivative|IsDerivedFrom],
                '@id': <related_object.uuid>
            }
        """
        if self._relationships is None:
            self._relationships = self.value.get('_relationships', [])

        return self._relationships

    @property
    def related_objects(self):
        """
        List objects related to this object.
        """
        if self._related_objects is None:
            self._related_objects = self._get_related_objects()

        return self._related_objects

    def add_relationship(self, relationship):
        """
        Add a relationship from an existing object to this object.

        Required parameter:
            relationship        # dictionary: { '@rel:type': ..., '@id' ... }

        Relationship Description:
            {
                'type': [HasPart|IsPartOf|HasDerivation|IsDerivedFrom],
                '@id': <related_object.uuid>
            }

        Returns None
        """
        if type(relationship) is not dict or \
                not all(key in ['@rel:type', '@id'] for key in relationship.keys()):
            raise Exception('Invalid relationship format.')

        self.relationships.append(relationship)

    def remove_relationship(self, relationship):
        """
        Remove a relationship from an existing object to this object.

        Required parameter:
            relationship        # dictionary: { '@rel:type': ..., '@id' ... }

        Relationship Description:
            {
                'type': [HasPart|IsPartOf|HasDerivation|IsDerivedFrom],
                'uuid': <related_object.uuid>
            }

        Returns None
        """
        if type(relationship) is not dict or\
                not all(key in ['@rel:type', '@id'] for key in relationship.key()):
            raise Exception('Invalid relationship format.')

        self.relationships.remove(relationship)
