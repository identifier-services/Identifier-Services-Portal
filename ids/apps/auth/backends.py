
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import logging, re, requests

class AgaveOAuthBackend(ModelBackend):

    logger = logging.getLogger(__name__)

    def authenticate(self, *args, **kwargs):
        user = None

        if 'backend' in kwargs and kwargs['backend'] == 'agave':
            token = kwargs['token']
            tenant_base_url = getattr(settings, 'AGAVE_TENANT_BASEURL')

            self.logger.info('Attempting login via Agave with token "{}"'.format(
                token[:8].ljust(len(token), '-')
            ))

            profile_url = '{}/profiles/v2/me'.format(tenant_base_url)
            header = {'Authorization': 'Bearer {}'.format(token)}

            response = request.get(profile_url, header)
            json_result = response.json()

            if 'status' in json_result and json_result['status'] == 'success':
                agave_user = json_result['result']
                username = agave_user['username']
                self.logger.info('User: "{}" has logged in.'.format(username))
                #user_model = get_user_nmodel()
            else:
                self.logger.info('Agave Authentication failed: {}'.format(json_result))

        return user
