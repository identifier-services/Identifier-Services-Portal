from base_metadata import BaseMetadata


class Dataset(BaseMetadata):
    name ='idsvc.dataset'

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
        super(Dataset, self).__init__(*args, **kwargs)

        self._project = None
        self._data = None
        self._identifiers = None

    @property
    def dataset_name(self):
        return self.value.get('dataset_name')

    @property
    def project(self):
        """Returns the project to which this dataset is assoicated"""
        if self._project is None:
            project = next(iter([x for x in self.my_associations if x.name == 'idsvc.project']), None)
            self._project = project
        return self._project

    @property
    def data(self):
        """Returns the data grouped by this dataset"""
        if self._data is None:
            data = [x for x in self.my_associations if x.name == 'idsvc.data']
            self._data = data
        return self._data

    def add_to_project(self, project):
        """
        Add this dataset to an existing project, which should be passed as a parameter
        """
        self._project = project
        self.add_association_to(project)

    def add_data(self, data):
        datas = self.data
        datas.append(data)
        self._data = datas
        self.add_association_to(data)

    @property
    def identifiers(self):
        if self._identifiers is None:
            identifiers = [x for x in self.associations_to_me if x.name == 'idsvc.identifier']
            self._identifiers = identifiers
        return self._identifiers

    def add_identifier(self, identifier):
        identifiers = self.identifiers
        identifiers.append(identifier)
        self._identifiers = identifiers
        self.add_association_from(identifier)
