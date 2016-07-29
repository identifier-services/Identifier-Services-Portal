from django.test import TestCase
from test_client import TestClient


class BaseClientTests(TestCase, TestClient):
    """Test class is inteded to be inherited"""

    # make sure we got the env variables

    def test_environ_tenant_baseurl(self):
        """Did we get the baseurl env variable?"""
        self.assertIsNotNone(self.AGAVE_TENANT_BASEURL)

    def test_environ_sys_token(self):
        """Did we get the ids sys super token env variable?"""
        self.assertIsNotNone(self.IDS_SYS_SUPER_TOKEN)

    def test_environ_testuser1_token(self):
        """Did we get the test user 1 env variable?"""
        self.assertIsNotNone(self.TEST_USER1_SUPER_TOKEN)

    def test_environ_testuser2_token(self):
        """Did we get the test user 2 env variable?"""
        self.assertIsNotNone(self.TEST_USER2_SUPER_TOKEN)

    # make sure we can use out clients

    def test_sys_client(self):
        """Test ids sys client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(self.IDS_SYS_CLIENT.profiles.listByUsername(username='me'))

    def test_testuser1_client(self):
        """Test test user 1 client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(self.TEST_USER1_CLIENT.profiles.listByUsername(username='me'))

    def test_testuser2_client(self):
        """Test test user 2 client, should return dict with username for profiles.listByUsername"""
        self.assertIsNotNone(self.TEST_USER2_CLIENT.profiles.listByUsername(username='me'))

    # def delete_meta(self):
    #     """Delete all projects with name = 'idsvc.project'"""
    #
    #     results = self.IDS_SYS_CLIENT.meta.listMetadata()
    #
    #     import pprint
    #     pprint.pprint(results)
    #
    #     for mo in results:
    #         try:
    #             self.IDS_SYS_CLIENT.meta.deleteMetadata(uuid=mo['uuid'])
    #         except Exception as e:
    #             print e
    #             print mo['uuid']
    #
    # def test_delete_meta(self):
    #     """Create a project, save it, and cleanup by deleting all projects"""
    #     self.delete_meta()
