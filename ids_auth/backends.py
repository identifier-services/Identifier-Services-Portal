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
            tenantBaseUrl = getattr(settings, 'AGAVE_TENANT_BASEURL')

            self.logger.info('Attempting login via Agave with token "%s"' %
                token[:8].ljust(len(token), '-'))

            response = requests.get('%s/profiles/v2/me' % tenantBaseUrl, headers={
                'Authorization': 'Bearer %s' % token
                })
            json_result = response.json()

            if 'status' in json_result and json_result['status'] == 'success':
                agave_user = json_result['result']
                username = agave_user['username']
                UserModel = get_user_model()

                try:

                    user = UserModel.objects.get(username=username)

                    if 'first_name' in agave_user:
                        user.first_name = agave_user['first_name']
                    elif 'firstName' in agave_user:
                        user.first_name = agave_user['firstName']

                    if 'last_name' in agave_user:
                        user.last_name = agave_user['last_name']
                    elif 'lastName' in agave_user:
                        user.last_name = agave_user['lastName']

                    user.email = agave_user['email']
                    user.save()

                except UserModel.DoesNotExist:
                    self.logger.info('Creating local user record for "%s" from Agave Profile' % username)

                    if 'first_name' in agave_user:
                        first_name = agave_user['first_name']
                    elif 'firstName' in agave_user:
                        first_name = agave_user['firstName']

                    if 'last_name' in agave_user:
                        last_name = agave_user['last_name']
                    elif 'lastName' in agave_user:
                        last_name = agave_user['lastName']

                    user = UserModel.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=agave_user['email']
                        )

                self.logger.info('Login successful for user "%s"' % username)
            else:
                self.logger.info('Agave Authentication failed: %s' % json_result)
        return user
