from django.test import TestCase
from django.http import HttpRequest
from django.test import Client, RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from github_leaderboard.users.models import User

import github_leaderboard.app.views as views
import github_leaderboard.app.models

# Create your tests here.
def test_http501():
    msg = "TEST"
    resp = views.http501(msg)
    assert resp.content == bytes(msg, 'utf-8')
    assert resp.status_code == 501

class DashboardViewTests(TestCase):

    URL = 'app/dashboard'

    # TODO: something about self.user is broken
    # Can't get models with it as attr
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpassword'
        )

    def test_invalid_method(self):
        ''' Test some invalid HTTP methods '''
        error_code = 404
        response = self.c.put(self.URL)
        assert response.status_code == error_code
        response = self.c.head(self.URL)
        assert response.status_code == error_code

    def test_get_method(self):
        ''' Test GET method with authenticated user '''
        # Setup
        ldb = github_leaderboard.app.models.Leaderboard()
        ldb.name = 'test_leaderboard'
        ldb.owner = self.user
        request = self.factory.get(self.URL)
        request.user = self.user
        # Get Response
        response = views.dashboard(request)
        assert response.status_code == 200

