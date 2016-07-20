from django.test import TestCase
from ..models import Project
from test_client import TestClient


def print_doc(func):
    def wrapper(*args, **kwargs):
        print func.__doc__
        return func(*args, **kwargs)
    return wrapper


class ProjectTests(TestCase, TestClient):
    """Tests for Project in IDS models"""

    @print_doc
    def save_project(self):
        """Reusable method for saving a project object"""

        project = Project(api_client=self.TEST_USER1_CLIENT)
        project.save()
        self.assertIsNotNone(project.uuid)
        self.assertIsNotNone(project.name)

        return project

    @print_doc
    def delete_project(self):
        """Delete all projects with name = 'idsvc.project'"""

        # get a list of all projects

        response = Project.list(api_client=self.TEST_USER1_CLIENT)

        # we will delete all projects owned by self.TEST_USER1_CLIENT

        for mo in response:
            mo.delete()

        response = Project.list(api_client=self.TEST_USER1_CLIENT)

        self.assertEqual(len(response), 0)

    @print_doc
    def test_save_project(self):
        """Create a project, save it, and cleanup by deleting all projects"""
        self.save_project()
        self.delete_project()

    @print_doc
    def test_list_projects(self):
        """Create a project, save it, list projects, cleanup by deleting all projects"""

        project = self.save_project()

        proj_list = Project.list(project._api_client)
        self.assertNotEqual(len(proj_list), 0)

        self.delete_project()
