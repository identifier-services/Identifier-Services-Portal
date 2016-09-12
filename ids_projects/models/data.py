from base_metadata import BaseMetadata
from system import System
from ids.utils import get_portal_api_client
import json
import logging

logger = logging.getLogger(__name__)


class Data(BaseMetadata):
    """ """
    name = 'idsvc.data'

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
        super(Data, self).__init__(*args, **kwargs)

        self.system = None
        system_id = kwargs.get('system_id')
        path = kwargs.get('path')
        sra_id = kwargs.get('sra_id')

        if system_id is not None:
            self.system_id = system_id
        else:
            self.system_id = self.value.get('system_id')

        if self.system_id is not None:
            self.value.update({'system_id': self.system_id})

        if path is not None:
            self.path = path
        else:
            self.path = self.value.get('path')

        if self.path is not None:
            self.value.update({'path': self.path})

        if sra_id is not None:
            self.sra_id = sra_id
        else:
            self.sra_id = self.value.get('sra_id')

        if self.sra_id is not None:
            self.value.update({'sra_id': self.sra_id})

    @property
    def title(self):
        file_name = self.value.get('name')
        if file_name:
            return file_name
        else:
            return self.sra_id

    @property
    def project(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.project']), None)

    @property
    def specimen(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.specimen']), None)

    @property
    def process(self):
        return next(iter([x for x in self.containers if x.name == 'idsvc.process']), None)

    @property
    def datasets(self):
        return [x for x in self.containers if x.name == 'idsvc.datasets']

    def load_file_info(self):
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
                self.system = System(api_client=self._api_client, system_id=self.system_id)
            except Exception as e:
                exception_msg = 'Unable to access system with system_id=%s.' % self.system_id
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

        self.value = file_info

    def _share(self, username, permission):
        """"""
        body=json.dumps({ 'username': username,
                          'permission': permission,
                          'recursive': False })
        self._api_client.files.updatePermissions(
                systemId=self.system_id,
                filePath=self.value['path'],
                body=body )

    def save(self):
        super(Data, self).save()

        if self.path and self.system_id:
            logger.debug('Sharing data with portal user...')
            self._share(username='idsvc_user', permission='READ')

    def calculate_checksum(self):
        """ """
        name = "checksum"
        app_id = "idsvc_checksum-0.1"
        archive = True

        portal_client = get_portal_api_client()

        if self.sra_id:
            parameters = {'UUID': self.uuid, 'SRA': self.sra_id}
            body = {'name': name, 'appId': app_id, 'parameters': parameters}
        else:
            agave_url = "agave://%s/%s" % (self.system_id, self.path)
            inputs = { 'AGAVE_URL': agave_url }
            parameters = { 'UUID': self.uuid }
            body={'name': name, 'appId': app_id, 'inputs': inputs, 'parameters': parameters, 'archive': archive}

        try:
            self.meta['value'].update(
                 {'checksum': None,
                  'lastChecksumUpdated': None,
                  'checksumConflict': None,
                  'checkStatus': None})
            self.save()
        except Exception as e:
            exception_msg = 'Unable to initiate job. %s' % e
            logger.error(exception_msg)
            raise Exception(exception_msg)

        try:
            logger.debug("Job submission body: %s" % body)

            import pprint
            pprint.pprint(body)

            # response = self._api_client.jobs.submit(body=body)
            response = portal_client.jobs.submit(body=body)

            logger.debug("Job submission response: %s" % response['id'])
        except Exception as e:
            exception_msg = 'Unable to initiate job. %s' % e
            logger.error(exception_msg)
            raise Exception(exception_msg)

        return response

    def delete(self):
        """Delete a data object, and remove relationships to it"""
        if self.uuid is None:
            raise Exception('Cannot delete without UUID.')

        # delete all objects that have this object's uuid in their associationIds
        for container in self.containers:
            logger.debug('removing part (%s): %s - %s, from container (%s): : %s - %s' %
                         (self.name, self.uuid, self.title, container.name, container.uuid, container.title))
            container.remove_part(self)
            container.save()

        logger.debug('deleting %s: %s - %s' % (self.name, self.uuid, self.title))

        try:
            self._api_client.meta.deleteMetadata(uuid=self.uuid)
        except Exception as e:
            logger.debug('Object does not exist, probably previously deleted. Error: %s' % e)

        self.uuid = None
