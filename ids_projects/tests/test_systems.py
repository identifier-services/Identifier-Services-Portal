from django.test import TestCase
from ..models import System
from test_client import TestClient

class SystemTests(TestCase, TestClient):
    def test_instantiate_system(self):
        """Create a system object"""
        system = System(api_client=self.IDS_SYS_CLIENT)
        self.assertIsNotNone(system)
        self.assertIsNotNone(system._api_client)
        self.assertEqual(system._api_client, self.IDS_SYS_CLIENT)

    def test_list_systems(self):
        """List all systems for client"""
        system_list = System.list(api_client=self.IDS_SYS_CLIENT, system_type="STORAGE")

        self.assertIsNotNone(system_list)
        self.assertTrue(any([sys.id == 'data.tacc.utexas.edu' for sys in system_list]))

        system_list = System.list(api_client=self.IDS_SYS_CLIENT, system_type="EXECUTION")

        self.assertIsNotNone(system_list)
        self.assertTrue(any([sys.id == 'lonestar5.tacc.utexas.edu' for sys in system_list]))

    def test_instantiate_specific_system(self):
        """Attempt to create a system object with call to Agave"""
        system_id = 'foobar-corral'

        system = System(api_client=self.IDS_SYS_CLIENT, system_id=system_id)

        self.assertIsNotNone(system)
        self.assertTrue(system.id == system_id)

    def test_directory_listing(self):
        """Test listing directory contents"""
        system_id = 'foobar-corral'

        system = System(api_client=self.IDS_SYS_CLIENT, system_id=system_id)

        path = '/'

        listing = system.listing(path)

        self.assertIsNotNone(listing)

        # import pprint
        # pprint.pprint(listing)

        # self.assertTrue(any([sys.id == 'lonestar5.tacc.utexas.edu' for sys in system_list]))
