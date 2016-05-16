from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from agavepy.agave import Agave
import json, logging

logger = logging.getLogger(__name__)


class BaseMetadata(object):

    def __init__(self, uuid=None, initial_data=None, user=None):
        self.system_ag = None
        self.user_ag = None
        self.user = None

        if user is not None:
            # if type(user) is not django.utils.functional.SimpleLazyObject:
            #     exception_msg = 'User parameter type is incorrect.'
            #     logging.exception(exception_msg)
            #     raise TypeError(exception_msg)

            self.user = user
            self.user_ag = self.get_client(user=user)

        try:
            self.system_ag = self.get_client()
        except Exception as e:
            exception_msg = 'Unable to connect to Agave as IDS system user. %s' % e
            logger.exception(exception_msg)
            raise Exception(exception_msg)

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

    def get_client(self, user=None):
        if user is not None:
            # if type(user) is not django.utils.functional.SimpleLazyObject:
            #     exception_msg = 'User parameter type is incorrect.'
            #     logging.exception(exception_msg)
            #     raise TypeError(exception_msg)

            # user client
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=self.user.agave_oauth.access_token)
        else:
            # system client
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=settings.AGAVE_SUPER_TOKEN)

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
            if self.value is None:
                self.value = initial_data['value']
            else:
                # i don't want to clear values that might not be contained in a form (like 'public':'True')
                for key, value in initial_data['value'].items():
                    self.value[key] = value

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
                debug_msg = 'Agave meta object not owned by logged in user. %s' % e
                logger.debug(debug_msg)
        else:
            # query public meta owned by system user
            try:
                # if public:
                #     query = { 'uuid': self.uuid, 'value.public': 'True' }
                # else:
                #     query = { 'uuid': self.uuid }
                query = { 'uuid': self.uuid }
                metas = self.system_ag.meta.listMetadata(q=json.dumps(query))
                meta = next(iter(metas), None)
            except Exception as e:
                exception_msg = 'Agave meta object not owned by system user. %s' % e
                logger.debug(exception_msg)

        if meta is None:
            exception_msg = 'Agave meta object not found.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        self.set_initial(meta)

    def save(self):
        # if no uuid, we are creating a new object (as the system user)
        if self.uuid is None:
            if self.user is None:
                exception_msg = 'Missing user information, cannot create object.'
                logger.exception(exception_msg)
                raise Exception(exception_msg)

            try:
                response = self.system_ag.meta.addMetadata(body=self.body)
                self.set_initial(response)
            except Exception as e:
                exception_msg = 'Unable to save object. %s' % e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

            try:
                self.system_ag.meta.updateMetadataPermissions(
                    uuid=self.uuid,
                    body={
                        'username': self.user.username,
                        'permission': 'READ_WRITE'
                    })

                self.set_initial(response)
            except Exception as e:
                # rollback
                self.system_ag.meta.deleteMetadata(uuid=self.uuid)
                exception_msg = 'Unable to update permissions, rolling back. %s' % e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

        # if we have a uuid, we are probably editing an existing object
        else:

            try:
                response = self.system_ag.meta.updateMetadata(uuid=self.uuid, body=self.body)
                self.set_initial(response)
            except Exception as e:
                exception_msg = 'Unable update object. %s' % e
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

    def list(self, public=False):
        results = None

        if public is True:
            try:
                query = {'name': Project.name, 'value.public': 'True'}
                results = self.system_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                exception_msg = 'Fatal exception: %s' % e
                logger.exception(e)
                raise e
        else:
            try:
                query = {'name': Project.name}
                results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                exception_msg = 'Unable to list metadata, user may not be logged in: %s' % e
                logger.debug(exception_msg)
        if results is not None:
            return [Project(initial_data = r, user=self.user) for r in results]
        else:
            return None

    @property
    def specimens(self, reset=False):
        if self._specimens is None or reset:
            query = {'associationIds': [self.uuid], 'name': Specimen.name}
            # TODO: return public and private results
            meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            self._specimens = [Specimen(initial_data=r) for r in meta_results]

        return self._specimens

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:
            query = {'associationIds': [self.uuid], 'name': Process.name}
            # TODO: return public and private results
            meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            self._processes = [Process(initial_data=r) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:
            query = {'associationIds': self.uuid, 'name': Data.name}
            # TODO: return public and private results
            meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            self._data = [Data(initial_data=r) for r in meta_results]

        return self._data

    @property
    def title(self):
        return self.value['title']

    @title.setter
    def title(self, new_title):
        self.value['title'] = new_title

    def _modify_access(self, public=True):
        if self.user_ag is None:
            exception_msg = 'Missing user client, cannot update object.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if self.uuid is None:
            exception_msg = 'Missing UUID, cannot update object.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            self.value['public'] = 'True' if public else 'False'
            self.save()
        except Exception as e:
            exception_msg = 'Unable update project. %s' % e
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        for uuid in self.associationIds:
            try:
                name = 'object'
                item = BaseMetadata(uuid=uuid, user=self.user)
                name = item.name
                item.value['public'] = 'True' if public else 'False'
                item.save()
            except Exception as e:
                exception_msg = 'Unable update %s. %s' % (name, e)
                logger.exception(exception_msg)
                raise Exception(exception_msg)

    def make_public(self):
        self._modify_access(public=True)

    def make_private(self):
        self._modify_access(public=False)


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
            # TODO: return public and private results
            results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            self._project = Project(initial_data = next(iter(results), None))

        return self._project

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:
            query = {'associationIds': self.uuid, 'name': Process.name}
            # TODO: return public and private results
            meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            self._processes = [Process(initial_data=r) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:
            query = {'associationIds': self.uuid, 'name': Data.name}
            # TODO: return public and private results
            meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
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
        resp = self.user_ag.jobs.submit(body={'appId': '<app id>', 'inputs': [], 'parameters': []})

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
        results = Project().user_ag.systems.list(type=system_type)
        return [cls(initial_data = r) for r in results]

    def load(self):
        meta = self.user_ag.systems.get(systemId=self.id)
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
            return self.user_ag.systems.add(fileToUpload=None)
        else:
            return self.user_ag.systems.update(systemId=self.id, body=None)

    def delete(self):
        #TODO: see if this works
        raise(NotImplemented)
        return self.user_ag.systems.delete(systemId=self.id)

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
