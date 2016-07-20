from django.test import TestCase
from django.core.urlresolvers import reverse
from test_client import TestClient
import mock


class ViewTests(TestCase):

    fixtures = ['user_data.json']

    def test_list_datasets_view(self):
        response = self.client.get(reverse('ids_projects:dataset-list-public'))
        self.assertContains(response, '<h1>Public Datasets</h1>')

    def test_list_user_projects_anon(self):
        response = self.client.get(reverse('ids_projects:project-list-private'))
        self.assertRedirects(response, '/login/?next=/projects/private', status_code=302,
                             fetch_redirect_response=False)

    @mock.patch('ids_projects.models.Project.list')
    def test_list_user_projects(self, mock_project_list):
        self.client.login(username='ids_user_1', password='testing')
        response = self.client.get(reverse('ids_projects:project-list-private'))

        assert mock_project_list.called
        self.assertContains(response, "<h3>User's Projects</h3>")
