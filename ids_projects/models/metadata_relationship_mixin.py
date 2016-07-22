import json


class MetadataRelationshipMixin(object):
    """Mixin with BaseMetadata"""

    #########
    # PARTS #
    #########

    @property
    def parts(self):
        """
        Get all objets that are part of this object ('HasPart' relationsip).
        """
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # TODO: cache more general query results, filter
        query = { 'value._relationships': { '$elemMatch': {'@id': self.uuid, '@rel:type': 'HasPart'} } }
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        parts = []

        for related_meta in results:
            related_object = self.get_class_by_name(related_meta.name)\
                            (meta=related_meta, api_client=self._api_client)
            parts.append(related_object)

        return parts

    def add_part(self, part_object):
        """
        Add an objets that is part of this object ('HasPart' relationsip).
        """
        if not 'uuid' in dir(part_object) or not part_object.uuid:
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
        Get all objects that this object belongs to ('IsPartOf' relationsip).
        """
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # TODO: cache more general query results, filter
        query = { 'value._relationships': { '$elemMatch': {'@id': self.uuid, '@rel:type': 'HasPart'} } }
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        containers = []

        for related_meta in results:
            related_object = self.get_class_by_name(related_meta.name)\
                (meta=related_meta, api_client=self._api_client)
            containers.append(related_object)

        return containers

    def add_container(self, container_object):
        """
        Add an objects that this object belongs to ('IsPartOf' relationsip).
        """
        if not 'uuid' in dir(container_object) or not container_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            'type': 'IsPartOf',
            '@id': container_object.uuid
        }

        self.add_relationship(relationship)

    ###############
    # DERIVATIONS #
    ###############

    @property
    def derivations(self):
        """
        Get all objects derived from this objects (name of relationship?).
        """
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # TODO: cache more general query results, filter
        query = { 'value._relationships': { '$elemMatch': {'@id': self.uuid, '@rel:type': 'DerivedFrom'} } }
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        derivations = []

        for related_meta in results:
            related_object = self.get_class_by_name(related_meta.name)\
                            (meta=related_meta, api_client=self._api_client)
            derivations.append(related_object)

        return derivations

    def add_derivation(self, derived_object):
        """
        Add an objects derived from this objects (name of relationship?).
        """
        if not 'uuid' in dir(derived_object) or not derived_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'HasDerivation',
            '@id': derived_object.uuid
        }

        self.add_relationship(relationship)

    ##############
    # PRECURSORS #
    ##############

    @property
    def precursors(self):
        """
        Get all objects that this object is derived from ('DerivedFrom' relationship).
        """
        if not self.uuid:
            raise Exception('Missing UUID, cannot look up relationships without UUID.')

        # TODO: cache more general query results, filter
        query = { 'value._relationships': { '$elemMatch': {'@id': self.uuid, '@rel:type': 'HasDerivations'} } }
        results = self._api_client.meta.listMetadata(q=json.dumps(query))

        precursors = []

        for related_meta in results:
            related_object = self.get_class_by_name(related_meta.name)\
                            (meta=related_meta, api_client=self._api_client)
            precursors.append(related_object)

        return precursors

    def add_precursor(self, precursor_object):
        """
        Get all objects that this object is derived from ('DerivedFrom' relationship).
        """
        if not 'uuid' in dir(precursor_object) or not precursor_object.uuid:
            raise Exception('Cannot add part, object does not contain UUID.')

        relationship = {
            '@rel:type': 'DerivedFrom',
            '@id': precursor_object.uuid
        }

        self.add_relationship(relationship)

    ################
    # RELATIONSIPS #
    ################

    @property
    def relationships(self):
        """
        List relationships to this object, in the form:
            {
                '@rel:type': [HasPart|IsPartOf|HasDerivation|IsDerivedFrom],
                '@id': <related_object.uuid>
            }
        """
        if self._relationships is None:
            self._relationships = self.value.get('_relationships', [])
        return self._relationships

    def add_relationship(self, relationship):
        """
        Add a relationship from and existing object to this object, in the form:

        Required parameter:
            relationship        # dictionary: { '@rel:type': ..., '@id' ... }

        relationship:
            {
                'type': [HasPart|IsPartOf|HasDerivation|IsDerivedFrom],
                '@id': <related_object.uuid>
            }
        """
        if type(relationship) is not dict or\
        not all(key in ['@rel:type','@id'] for key in relationship.key()):
            raise Exception('Invalid relationship format.')

        rels = self.relationships
        rels.extend(relationship)

        self._relationships = rels

    def remove_relationship(self, relationship):
        """
        Add a relationship from and existing object to this object, in the form:

        Required parameter:
            relationship        # dictionary: { '@rel:type': ..., '@id' ... }

        relationship:
            {
                'type': [HasPart|IsPartOf|HasDerivation|IsDerivedFrom],
                'uuid': <related_object.uuid>
            }
        """
        if type(relationship) is not dict or\
        not all(key in ['@rel:type','@id'] for key in relationship.key()):
            raise Exception('Invalid relationship format.')

        self._relationships.remove(relationship)
