from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from agavepy.agave import Agave
import json, logging

logger = logging.getLogger(__name__)


class BaseMetadata(object):

    def __init__(self, uuid=None, initial_data=None):
        self.system_ag = None
        self.user_ag = None

        try:
            self.system_ag = get_client(as_system=True)
        except Exception as e:
            # this is a fatal exception
            exception_msg = 'Unable to connect to Agave as IDS system user.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            self.user_ag = get_client(as_system=False)
        except Exception as e:
            # this is not a fatal exception
            debug_msg = 'User is not logged in.'
            logger.debug(debug_msg)

        self.associationIds = None
        self.created = None
        self.lastUpdated = None
        self.links = None
        self.value = None
        self.uuid = uuid

        if uuid is not None:
            self.load()

        if initial_data is not None:
            self.set_initial(initial_data)

    def get_client(self, as_system):
        if as_system:
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=settings.AGAVE_SUPER_TOKEN)
        else:
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=self.user.agave_oauth.access_token)

    def set_initial(self, initial_data):
        if 'uuid' in initial_data:
            self.uuid = initial_data['uuid']
        if 'associationIds' in initial_data:
            self.associationIds = initial_data['associationIds']
        if 'created' in initial_data:
            self.created = initial_data['created']
        if 'lastUpdated' in initial_data:
            self.lastUpdated = initial_data['lastUpdated']
        if '_links' in initial_data:
            self.links = initial_data['_links']
        if 'value' in initial_data:
            self.value = initial_data['value']

    def load(self):
        if self.uuid is None:
            exception_msg = 'No UUID provided, Agave meta object not found.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        meta = None

        if self.user_ag is not None:
            # query meta owned by logged in user
            try:
                meta = self.user_ag.meta.getMetadata(uuid=self.uuid)
            except Exception as e:
                self.uuid = None
                exception_msg = 'Agave meta object not owned by logged in user.'
                logger.debug(exception_msg)
        else:
            # query public meta owned by system user
            try:
                query = { 'uuid': self.uuid, 'value.public': 'True' }
                metas = self.system_ag.meta.listMetadata(q=json.dumps(query))
                meta = next(iter(metas), None))
            except Exception as e:
                exception_msg = 'Agave meta object not owned by system user.'
                logger.debug(exception_msg)

        if meta is None:
            exception_msg = 'Invalid UUID provided, Agave meta object not found.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        self.set_initial(meta)

    def save(self):
        if self.user_ag is None:
            exception_msg = 'User is not logged in, cannot save object.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        # if no uuid, we are creating a new object (as the system user)
        if self.uuid is None:
            try:
                response = self.system_ag.meta.addMetadata(body=self.body)
                # update permissions to include the logged in user
                self.system_ag.meta.updateMetadataPermissions(uuid=response['uuid'], body={
                    'user': self.user.username,
                    # 'permission': 'READ_WRITE',
                    'permission': 'ALL',
                    # I'm going to set permissions for the logged in user to
                    # 'ALL', because I want to the use the logged in user
                    # (not the system user) to delete the meta objects. If we
                    # use the system user to delete meta objects, we'll have
                    # to check to make sure the logged in user isn't deleting
                    # public data that they shouldn't, and that's too complicated.
                })
                self.set_initial(response['result'])
            except Exception as e:
                exception_msg = 'Unable to save object. %s' e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

        # if we have a uuid, we are probably editing an existing object
        else:
            try:
                response = self.user_ag.meta.updateMetadata(uuid=self.uuid, body=self.body)
                self.set_initial(response['result'])
            except Exception as e:
                exception_msg = 'Unable update object. %s' e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

        return response

    def delete(self):
        if self.uuid is None:
            exception_msg = 'No UUID provided, no meta to delete.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if self.user_ag is None:
            exception_msg = 'User must be logged in to delete meta objects.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            # we use the logged in user to delete the meta object
            self.user_ag.meta.deleteMetadata(uuid=self.uuid)
            self.uuid = None
        except Exception as e:
            exception_msg = 'Unable to delete meta object. %s' % e
            logger.exception(exception_msg)
            raise Exception(exception_msg)

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
        projects = [cls(initial_data = r) for r in results]
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
            self._project = Project(initial_data = next(iter(results), None))

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

    def calculate_checksum(self):
        # using AgavePy, submit job to run analysis
        resp = self.ag.jobs.submit(body={'appId': '<app id>', 'inputs': [], 'parameters': []})

        pass

class System(object):

    def __init__(self, system_id=None, initial_data=None):
        self.ag = Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                        token=settings.AGAVE_SUPER_TOKEN)
        self.id = None
        self.name = None
        self.type = None
        self.description = None
        self.status = None
        self.public = None
        self.default = None
        self._links = None

        if system_id is not None:
            self.id = system_id
            self.load()

        if initial_data is not None:
            self.set_initial(initial_data)

    def set_initial(self, initial_data):
        if 'id' in initial_data:
            self.id = initial_data['id']
        if 'name' in initial_data:
            self.name = initial_data['name']
        if 'type' in initial_data:
            self.type = initial_data['type']
        if 'description' in initial_data:
            self.description = initial_data['description']
        if 'status' in initial_data:
            self.status = initial_data['status']
        if 'public' in initial_data:
            self.public = initial_data['public']
        if 'default' in initial_data:
            self.default = initial_data['default']
        if '_links' in initial_data:
            self._links = initial_data['_links']

    @classmethod
    def list(cls, system_type="STORAGE"):
        results = Project().ag.systems.list(type=system_type)
        systems =  [cls(initial_data = r) for r in results]
        return [system.body for system in systems]

    def load(self):
        meta = self.ag.systems.get(systemId=self.id)
        self.set_initial(meta)

    def save(self):
        # {
        # 	"id": "demo.execute.example.com",
        # 	"name": "Demo SGE + GSISSH demo vm",
        # 	"status": "UP",
        # 	"type": "EXECUTION",
        # 	"description": "My example system using gsissh and gridftp to submit jobs used for testing.",
        # 	"site": "example.com",
        # 	"executionType": "HPC",
        # 	"queues": [
        # 		{
        # 			"name": "debug",
        # 			"maxJobs": 100,
        # 			"maxUserJobs": 10,
        # 			"maxNodes": 128,
        # 			"maxMemoryPerNode": "2GB",
        # 			"maxProcessorsPerNode": 128,
        # 			"maxRequestedTime": "24:00:00",
        # 			"customDirectives": "",
        # 			"default": true
        # 		}
        # 	],
        # 	"login": {
        # 		"host": "gsissh.example.com",
        # 		"port": 2222,
        # 		"protocol": "GSISSH",
        # 		"scratchDir": "/scratch",
        # 		"workDir": "/work",
        # 		"auth": {
        # 			"username": "demo",
        # 			"password": "demo",
        # 			"credential": "",
        # 			"type": "X509",
        # 			"server": {
        # 				"id": "myproxy.teragrid.org",
        # 				"name": "XSEDE MyProxy Server",
        # 				"site": "ncsa.uiuc.edu",
        # 				"endpoint": "myproxy.teragrid.org",
        # 				"port": 7512,
        # 				"protocol": "MYPROXY"
        # 			}
        # 		}
        # 	},
        # 	"storage": {
        # 		"host": "gridftp.example.com",
        # 		"port": 2811,
        # 		"protocol": "GRIDFTP",
        # 		"rootDir": "/home/demo",
        # 		"homeDir": "/",
        # 		"auth": {
        # 			"username": "demo",
        # 			"password": "demo",
        # 			"credential": "",
        # 			"type": "X509",
        # 			"server": {
        # 				"id": "myproxy.teragrid.org",
        # 				"name": "XSEDE MyProxy Server",
        # 				"site": "ncsa.uiuc.edu",
        # 				"endpoint": "myproxy.teragrid.org",
        # 				"port": 7512,
        # 				"protocol": "MYPROXY"
        # 			}
        # 		}
        # 	},
        # 	"maxSystemJobs": 100,
        # 	"maxSystemJobsPerUser": 10,
        # 	"scheduler": "SGE",
        # 	"environment": "",
        # 	"startupScript": "./bashrc"
        # }
        #TODO: implement system save
        raise(NotImplementedError)
        if self.id is None:
            return self.ag.systems.add(fileToUpload=None)
        else:
            return self.ag.systems.update(systemId=self.id, body=None)

    def delete(self):
        #TODO: see if this works
        raise(NotImplemented)
        return self.ag.systems.delete(systemId=self.id)

    @property
    def body(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'type' : self.type,
            'description' : self.description,
            'status' : self.status,
            'public' : self.public,
            'default' : self.default,
            '_links' : self._links,
        }
