from .base_metadata import BaseMetadata


class Project(BaseMetadata):
    """ """
    name = 'idsvc.project'

    def __init__(self, *args, **kwargs):
        """
        Required Parameter:
            api_client      # AgavePy client
        Optional Parameters:
            uuid            # unique identifier for existing metadata object
            body            # information held in metadata 'value' field
            meta            # json or dictionary, values may include:
                            #   uuid, owner, schemaId, internalUsername,
                            #   associationIds, lastUpdated, name, value,
                            #   created, _links
        Explicit parameters take precedence over values found in the meta dictionary
        """
        super(Project, self).__init__(*args, **kwargs)

    @property
    def title(self):
        return self.value.get('title')

    @property
    def specimens(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.specimen']

    @property
    def processes(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.process']

    @property
    def data(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.data']

    @property
    def datasets(self):
        return [x for x in self.associations_to_me if x.name == 'idsvc.dataset']
