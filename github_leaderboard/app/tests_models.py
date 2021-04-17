from django.test import TestCase
from django.http import HttpRequest
from django.test import Client, RequestFactory, TestCase
# from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from django.contrib.messages.storage.fallback import FallbackStorage

from github_leaderboard.users.models import User

import github_leaderboard.app.views as views
import github_leaderboard.app.models
import datetime as dt
import pytz
# from datetime import datetime

# Create your tests here.

def setup_view(view, request, *args, **kwargs):
    """
    Mimic ``as_view()``, but returns view instance.
    Use this function to get view instances on which you can run unit tests,
    by testing specific methods.
    """

    view.request = request
    view.args = args
    view.kwargs = kwargs
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return view

class LeaderboardModelTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpassword'
        )
        self.leaderboard = github_leaderboard.app.models.Leaderboard()
        self.leaderboard.id = 22
        self.leaderboard.name = 'test_leaderboard'
        self.leaderboard.owner = self.user
        self.leaderboard.repo_url = "https://github.com/jacksonet00/github-leaderboard"
        self.leaderboard.save()
        
    def test_leaderboard_refresh(self):
        ''' Test method test_leaderboard_refresh for updation of leaderboard commit data'''
        success = self.leaderboard.refresh()
        print(success)
    
    def test_get_ranked_user_commit_data(self):
        ''' Test method get_ranked_user_commit_data for given leaderboard'''
        data = self.leaderboard.get_ranked_user_commit_data()
        print(data)
    
    def test_close_if_ended(self):
        ''' Test if Ended Leaderboards are Closed using method test_close_if_ended'''
        today = pytz.UTC.localize(dt.datetime.now()) 
        self.leaderboard.closed = False
        self.leaderboard.start = today - dt.timedelta(days=15)
        self.leaderboard.end = today - dt.timedelta(days=7)

        self.leaderboard.close_if_ended()
        assert self.leaderboard.closed == True
        # print(self.leaderboard.closed)

