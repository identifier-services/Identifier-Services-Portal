import json


class MetadataRelationshipMixin(object):
    """Mixin with BaseMetadata"""

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
        # Query related objects that have IsPartOf type relationships to this object.
        return [x for x in self.relationships
                if x.value['_relationships']['@id'] == self.uuid
                and x.value['_relationships']['@rel:type'] == 'IsPartOf']

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
        return [x for x in self.relationships
                if x.value['_relationships']['@id'] == self.uuid
                and x.value['_relationships']['@rel:type'] == 'HasPart']

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
            'type': 'IsPartOf',
            '@id': container_object.uuid
        }

        self.add_relationship(relationship)

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
        return [x for x in self.relationships
                if x.value['_relationships']['@id'] == self.uuid
                and x.value['_relationships']['@rel:type'] == 'IsDerivedFrom']

    def add_derivative(self, derived_object):
        """
        Add an object that is derived from this objects.

        Relationship:

            This Object: HasDerivative: Related Object
            Related Object: IsDerivedFrom: This Object

        Returns None
        """
        if not 'uuid' in dir(derived_object) or not derived_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasDerivative',
            '@id': derived_object.uuid
        }

        self.add_relationship(relationship)

    ##############
    # PRECURSORS #
    ##############

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
        return [x for x in self.relationships
                if x.value['_relationships']['@id'] == self.uuid
                and x.value['_relationships']['@rel:type'] == 'HasDerivative']

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

    #################
    # RELATIONSHIPS #
    #################

    def _get_relationships(self):
        """Internal method, queries agave tenant for all related objects, returns list."""
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # get all objects with relationship to this object.
        query = { 'value._relationships': { '$elemMatch': {'@id': self.uuid } } }
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        related_objects = []

        for related_meta in results:
            # instantiate related objects
            related_object = self.get_class_by_name(related_meta.name)\
                            (meta=related_meta, api_client=self._api_client)

            # append to list
            related_objects.append(related_object)

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
            self._relationships = self._get_relationships()

        return self._relationships

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
                not all(key in ['@rel:type', '@id'] for key in relationship.key()):
            raise Exception('Invalid relationship format.')

        self.relationships.extend(relationship)

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
