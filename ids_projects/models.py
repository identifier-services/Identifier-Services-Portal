from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from agavepy.agave import Agave
import json, logging

logger = logging.getLogger(__name__)


class BaseClient(object):
    def __init__(self, user=None, *args, **kwargs):
        self.system_ag = None
        self.user_ag = None
        self.user = None

        if user is not None:
            if type(user) is not SimpleLazyObject:
                exception_msg = 'User parameter type is incorrect.'
                logging.error(exception_msg)
                raise TypeError(exception_msg)

            self.user = user
            if not user.is_anonymous():
                self.user_ag = self.get_client(user=user)

        try:
            self.system_ag = self.get_client()
        except Exception as e:
            exception_msg = 'Unable to connect to Agave as IDS system user. %s' % e
            logger.exception(exception_msg)
            raise Exception(exception_msg)

    def get_client(self, user=None):
        if user is not None:
            if type(user) is not SimpleLazyObject:
                exception_msg = 'User parameter type is incorrect.'
                logging.error(exception_msg)
                raise TypeError(exception_msg)

            # user client
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=self.user.agave_oauth.access_token)
        else:
            # system client
            return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                         token=settings.AGAVE_SUPER_TOKEN)


class BaseMetadata(BaseClient):

    name = 'idsvc.object'

    def __init__(self, uuid=None, initial_data=None, *args, **kwargs):
        super(BaseMetadata, self).__init__(*args, **kwargs)
        self.contributors = None
        # this is a workaround until i figure out how to authenticate user through webhook
        self.public = kwargs.get('public', True)

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

    def set_initial(self, initial_data):
        if 'uuid' in initial_data:
            self.uuid = initial_data['uuid']
            self.load_contributors()
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

        meta_result = None

        if self.user_ag is not None:
            # query meta owned by logged in user
            try:
                meta_result = self.user_ag.meta.getMetadata(uuid=self.uuid)
            except Exception as e:
                debug_msg = 'Agave meta object not owned by logged in user.'
                logger.debug(debug_msg)

        if meta_result is None:
            # query public meta owned by system user
            try:
                # this is a workaround until i figure out how to authenticate user through webhook
                if self.public:
                    query = { 'uuid': self.uuid, 'value.public': 'True' }
                    meta_results = self.system_ag.meta.listMetadata(q=json.dumps(query))
                    meta_result = next(iter(meta_results), None)
                else:
                    meta_result = self.system_ag.meta.getMetadata(uuid=self.uuid)

            except Exception as e:
                exception_msg = 'Agave meta object not owned by system user. %s' % e
                logger.debug(exception_msg)

        if meta_result is None:
            # i want to remove the uuid if the meta doesn't load, to avoid
            # potentially editing and losing data. this is probably an unlikely
            # scenario, so i might chage my mind on this.
            self.uuid = None
            exception_msg = 'Agave meta object not found.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        self.set_initial(meta_result)
        self.load_contributors()

    @classmethod
    def make(cls, uuid=None, initial_data=None, user=None, *args, **kwargs):
        return cls(uuid, initial_data, user, *args, **kwargs)

    def list(self, public=False):
        results = None

        if public is True:
            try:
                query = {'name': self.name, 'value.public': 'True'}
                results = self.system_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                exception_msg = 'Fatal exception: %s' % e
                logger.exception(exception_msg)
                raise e
        else:
            try:
                query = {'name': self.name}
                results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                exception_msg = 'Unable to list metadata, user may not be logged in: %s' % e
                logger.debug(exception_msg)
        if results is not None:
            return [self.make(initial_data = r, user=self.user) for r in results]
        else:
            return None

    def _list_associated_meta(self, name, relationship):

        if relationship == 'parent':
            query = { 'uuid': { '$in': self.associationIds } }
        elif relationship == 'child':
            query = { 'associationIds': self.uuid }
        else:
            warning_msg = 'Cannot list associated meta, missing relationship type. Must be either parent or child.'
            logger.warning(warning_msg)
            return None

        if name is not None:
            query['name'] = name

        meta_results = None

        if self.user_ag is not None:
            try:
                # query meta owned by logged in user
                meta_results = self.user_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                debug_msg = 'Unable to list meta objects as logged in user. %s' % e
                logger.debug(debug_msg)

        if not meta_results:
            try:
                query['value.public'] = 'True'
                # query public meta owned by system user
                meta_results = self.system_ag.meta.listMetadata(q=json.dumps(query))
            except Exception as e:
                debug_msg = 'Unable to list meta objects as system user. %s' % e
                logger.debug(debug_msg)

        return meta_results

    def save(self):
        # if no uuid, we are creating a new object (as the system user)
        if self.uuid is None:
            if self.user is None:
                exception_msg = 'Missing user information, cannot create object.'
                logger.exception(exception_msg)
                raise Exception(exception_msg)

            try:
                # always create objects with the system user
                response = self.system_ag.meta.addMetadata(body=self.body)
                self.set_initial(response)
            except Exception as e:
                exception_msg = 'Unable to save object. %s' % e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

            try:
                # then grant permissions to the logged in user
                perm_result = self.system_ag.meta.updateMetadataPermissions(
                    uuid=self.uuid,
                    body={
                        'username': self.user.username,
                        'permission': 'READ_WRITE'
                    })

                self.contributors = [self.user.username]
                # TODO: should we add idsvc_user? not sure

                self.set_initial(response)
            except Exception as e:
                # rollback
                self.system_ag.meta.deleteMetadata(uuid=self.uuid)
                exception_msg = 'Unable to update permissions, rolling back. %s' % e
                logger.exception(exception_msg)
                raise Exception(exception_msg)

        # if we have a uuid, we are probably editing an existing object
        else:

            # in most cases we want to do this as the logged in user,
            # but a bug (#?) in the agave api prevents us from doing that
            # for now. so we'll use the system user, but we want to make
            # sure that the logged in user has privs

            if not self.user_is_contributor:
                if self.public:
                    exception_msg = 'Unable update object.'
                    logger.exception(exception_msg)
                    raise Exception(exception_msg)
                else:
                    # this is annoying workaround until agave permissions bug is fixed
                    pass
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

    def load_contributors(self):
        try:
            contributor_list = []
            permissions_list = self.system_ag.meta.listMetadataPermissions(uuid=self.uuid)
            for entry in permissions_list:
                if entry['permission']['write'] is True:
                    contributor_list.append(entry['username'])
            self.contributors = contributor_list
        except Exception as e:
            self.contributors = None
            exception_msg = 'Unable to list permissions on object. %s' % e
            logger.exception(exception_msg)

    @property
    def user_is_contributor(self):
        try:
            return self.user.username in self.contributors
        except Exception as e:
            exception_msg = "Missing user client. %s" % e
            logger.exception(exception_msg)
            return False

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

    @property
    def specimens(self, reset=False):
        if self._specimens is None or reset:

            meta_results = self._list_associated_meta(name=Specimen.name, relationship='child')
            self._specimens = [Specimen(initial_data=r, user=self.user) for r in meta_results]

        return self._specimens

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:

            meta_results = self._list_associated_meta(name=Process.name, relationship='child')
            self._processes = [Process(initial_data=r, user=self.user) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:

            meta_results = self._list_associated_meta(name=Data.name, relationship='child')
            self._data = [Data(initial_data=r, user=self.user) for r in meta_results]

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

        for item in self.specimens + self.processes + self.data:
            try:
                item.value['public'] = 'True' if public else 'False'
                item.save()
            except Exception as e:
                exception_msg = 'Unable update %s. %s' % (item.name, e)
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

            meta_results = self._list_associated_meta(name=Project.name, relationship='parent')
            self._project = Project(initial_data = next(iter(meta_results), None), user=self.user)

        return self._project

    @property
    def processes(self, reset=False):
        if self._processes is None or reset:

            meta_results = self._list_associated_meta(name=Process.name, relationship='child')
            self._processes = [Process(initial_data=r, user=self.user) for r in meta_results]

        return self._processes

    @property
    def data(self, reset=False):
        if self._data is None or reset:

            meta_results = self._list_associated_meta(name=Data.name, relationship='child')
            self._data = [Data(initial_data=r, user=self.user) for r in meta_results]

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
        if self.value is None:
            self.value = {}
        if not '_inputs' in self.value:
            self.value['_inputs'] = []
        if not '_outputs' in self.value:
            self.value['_outputs'] = []

    @property
    def project(self, reset=False):
        if self._project is None or reset:

            meta_results = self._list_associated_meta(name=Project.name, relationship='parent')
            self._project = Project(initial_data = next(iter(meta_results), None), user=self.user)

        return self._project

    @property
    def specimen(self, reset=False):
        if self._specimen is None or reset:

            meta_results = self._list_associated_meta(name=Specimen.name, relationship='parent')
            self._specimen = Specimen(initial_data = next(iter(meta_results), None), user=self.user)

        return self._specimen

    @property
    def data(self, reset=False):
        if self._data is None or reset:

            meta_results = self._list_associated_meta(Data.name, relationship='child')
            self._data = [Data(initial_data=r, user=self.user) for r in meta_results]

        return self._data

    @property
    def inputs(self):
        x = [Data(uuid=uuid, user=self.user) for uuid in self.value['_inputs']]
        return x

    @property
    def outputs(self):
        x = [Data(uuid=uuid, user=self.user) for uuid in self.value['_outputs']]
        return x


class Data(BaseMetadata):

    name = 'idsvc.data'

    def __init__(self, system_id=None, path=None, *args, **kwargs):
        # import pdb; pdb.set_trace()
        super(Data, self).__init__(*args, **kwargs)

        self._project = None
        self._specimen = None
        self._process = None
        self.system = None

        if system_id is None:
            system_id = self.value.get('system', None)

        self.system_id = system_id

        if path is None:
            path = self.value.get('path', None)

        self.path = path

        if self.system_id is not None \
           and self.path is not None \
           and self.public:
            self.load_file_info()

    def load_file_info(self):
        if self.user_ag is None:
            exception_msg = 'Missing user client, cannot load file info.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if self.system_id is None:
            exception_msg = 'Missing system id, cannot load file info.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if self.path is None:
            exception_msg = 'Missing file path, cannot load file info.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if self.system is None:
            try:
                self.system = System(system_id=self.system_id, user=self.user)
            except Exception as e:
                exception_msg = 'Unable to access system with system_id=%s.' % system_id
                logger.error(exception_msg)
                raise Exception(exception_msg)

        try:
            listing = self.system.listing(self.path)
            file_info = next(iter(listing), None)
        except Exception as e:
            exception_msg = 'The path=%s could not be listed on system=%s. %s' \
                            % (self.path, self.system_id, e)
            logger.error(exception_msg)
            raise Exception(exception_msg)

        try:
            last_mod = file_info['lastModified']
            file_info['lastModified'] = last_mod.strftime('%b %-d %I:%M')
        except:
            warning_msg = 'Listing response does not contain lastModified.'
            logger.warning(warning_msg)

        self.set_initial({ 'value': file_info })

    @property
    def project(self, reset=False):
        if self._project is None or reset:

            meta_results = self._list_associated_meta(name=Project.name, relationship='parent')
            self._project = Project(initial_data = next(iter(meta_results), None), user=self.user)

        return self._project

    @property
    def specimen(self, reset=False):
        if self._specimen is None or reset:

            meta_results = self._list_associated_meta(name=Specimen.name, relationship='parent')
            self._specimen = Specimen(initial_data = next(iter(meta_results), None), user=self.user)

        return self._specimen

    @property
    def process(self, reset=False):
        if self._process is None or reset:

            meta_results = self._list_associated_meta(name=Process.name, relationship='parent')
            self._process = Process(initial_data = next(iter(meta_results), None), user=self.user)

        return self._process

    def calculate_checksum(self):
        name = "checksum"
        app_id = "idsvc_checksum-0.1"
        archive = False
        agave_url = "agave://%s/%s" % (self.system_id, self.path)
        inputs = { 'AGAVE_URL': agave_url }
        parameters = { 'UUID': self.uuid }
        body={'name': name, 'appId': app_id, 'inputs': inputs, 'parameters': parameters}
        # using AgavePy, submit job to run analysis
        try:
            logger.debug("Job submission body: %s" % body)
            resp = self.system_ag.jobs.submit(body=body)
            logger.debug("Job submission response: %s" % resp)
        except Exception as e:
            exception_msg = 'Unable to initiate job. %s' % e
            logger.error(exception_msg)
            raise Exception(exception_msg)


class System(BaseClient):

    def __init__(self, system_id=None, initial_data=None, *args, **kwargs):

        super(System, self).__init__(*args, **kwargs)
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

    def list(self, system_type="STORAGE"):
        if self.user_ag is None:
            exception_msg = 'Missing user client, cannot list systems.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            results = self.user_ag.systems.list(type=system_type)
        except Exception as e:
            exception_msg = 'Unable to list systems. %s' % e
            logger.debug(exception_msg)
            raise e

        return [System(initial_data = r) for r in results]

    def listing(self, path):

        if not self.id:
            exception_msg = 'Missing system id, cannot list files.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        if not self.user_ag:
            exception_msg = 'Missing user client, cannot list files.'
            logger.exception(exception_msg)
            raise Exception(exception_msg)

        try:
            results = self.user_ag.files.list(systemId=self.id, filePath=path)
            return results
        except Exception as e:
            exception_msg = 'Unable to list files. %s' % e
            logger.debug(exception_msg)
            raise e

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
