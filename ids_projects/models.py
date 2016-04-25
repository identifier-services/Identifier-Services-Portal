from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from agavepy.agave import Agave
import json

class BaseMetadata(object):

    def __init__(self, uuid=None, initial_data=None):
        self.ag = Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                        token=settings.AGAVE_SUPER_TOKEN)

        self.uuid = None
        self.associationIds = None
        self.created = None
        self.lastUpdated = None
        self.links = None
        self.value = None

        if uuid is not None:
            self.uuid = uuid
            self.load()

        if initial_data is not None:
            self.set_values(initial_data)

    def set_values(self, metadata):
        self.uuid = metadata['uuid']
        self.associationIds = metadata['associationIds']
        self.created = metadata['created']
        self.lastUpdated = metadata['lastUpdated']
        self.links = metadata['_links']
        self.value = metadata['value']

    def load(self):
        meta = self.ag.meta.getMetadata(uuid=self.uuid)
        self.set_values(meta)

    def save(self):
        if self.uuid is None:
            self.ag.meta.addMetadata(body=self.body)
        else:
            self.ag.meta.updateMetadata(uuid=self.uuid, body=self.body)

    @property
    def body(self):
        return {
            'uuid': self.uuid,
            'associationIds': self.associationIds,
            'name': self.name,
            'value': self.value
        }


class Project(BaseMetadata):

    name = 'idsvc.project'

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self._specimens = None
        self._processes = None
        self._data = None

    @classmethod
    def list(cls):
        query = {'name': cls.name}
        results = Project().ag.meta.listMetadata(q=json.dumps(query))
        projects =  [cls(initial_data = r) for r in results]
        return [project.body for project in projects]

    @property
    def specimens(self, reset=False):
        if self._specimens is None or reset:
            query = {'associationIds': [self.uuid], 'name': Specimen.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._specimens = [Specimen(initial_data=r) for r in meta_results]

        return self._specimens

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:
            query = {'associationIds': [self.uuid], 'name': Process.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._processes = [Process(initial_data=r) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:
            query = {'associationIds': self.uuid, 'name': Data.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._data = [Data(initial_data=r) for r in meta_results]

        return self._data

    @property
    def title(self):
        return self.value['title']

    @title.setter
    def title(self, new_title):
        self.value['title'] = new_title


class Specimen(BaseMetadata):

    name = 'idsvc.specimen'

    def __init__(self, *args, **kwargs):
        super(Specimen, self).__init__(*args, **kwargs)
        self._project = None
        self._processes = None
        self._data = None

    @property
    def project(self, reset=False):
        if self._project is None or reset:
            associationIds = self.body['associationIds']
            query = {'uuid': { '$in': associationIds }, 'name': Project.name}
            results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._project = Project(initial_data = next(iter(results)))

        return self._project

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:
            query = {'associationIds': self.uuid, 'name': Process.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._processes = [Process(initial_data=r) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:
            query = {'associationIds': self.uuid, 'name': Data.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._data = [Data(initial_data=r) for r in meta_results]

        return self._data


class Process(BaseMetadata):
    """
    Sample value:
    {
        "assembly_method": "testing 789",
        "process_type": "sequencing",
        "reference_sequence": "testing asdf",
        "sequence_hardware": "testing 456",
        "sequence_method": "testing 123",
        "_inputs": ["<idsvc.data.uuid>", "<idsvc.data.uuid>"],
        "_outputs": ["<idsvc.data.uuid>"],
    }

    Where _inputs and _outpus are lists of metadata uuids for metadata objects
    name="idsvc.data".
    """

    name = 'idsvc.process'

    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(*args, **kwargs)
        self._project = None
        self._specimen = None
        self._data = None
        self._inputs = None
        self._outputs = None

    @property
    def project(self, reset=False):
        if self._project is None or reset:
            associationIds = self.body['associationIds']
            query = {'uuid': { '$in': associationIds }, 'name': Project.name}
            results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._project = Project(initial_data = next(iter(results)))

        return self._project

    @property
    def specimen(self, reset=False):
        if self._specimen is None or reset:
            associationIds = self.body['associationIds']
            query = {'uuid': { '$in': associationIds }, 'name': Specimen.name}
            results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._specimen = Specimen(initial_data = next(iter(results)))

        return self._specimen

    @property
    def data(self, reset=False):
        if self._data is None or reset:
            query = {'associationIds': self.uuid, 'name': Data.name}
            meta_results = self.ag.meta.listMetadata(q=json.dumps(query))
            self._data = [Data(initial_data=r) for r in meta_results]

        return self._data

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = [d for d in self.data if d.uuid in self.value['_inputs']]

        return self._inputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = [d for d in self.data if d.uuid in self.value['_outputs']]

        return self._outputs


class Data(BaseMetadata):

    name = 'idsvc.data'

    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
