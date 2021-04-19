from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

import github_leaderboard.app.models
import github_leaderboard.app.views as views
from github_leaderboard.users.models import User


def setup_view(view, request, *args, **kwargs):
    """
    Mimic ``as_view()``, but returns view instance.
    Use this function to get view instances on which you can run unit tests,
    by testing specific methods.
    """

    view.request = request
    view.args = args
    view.kwargs = kwargs
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return view


class LeaderboardViewTests(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@test.com", password="testpassword"
        )
        self.leaderboard = github_leaderboard.app.models.Leaderboard()
        self.leaderboard.id = 1
        self.leaderboard.name = "test_leaderboard"
        self.leaderboard.owner = self.user
        self.leaderboard.repo_url = "https://github.com/jacksonet00/github-leaderboard"
        self.leaderboard.save()

    def test_leaderboard_refresh_view(self):
        """ Test GET method for refresh leaderboard with authenticated user """

        request = self.factory.get(
            reverse("leaderboard_refresh", kwargs={"id": self.leaderboard.id})
        )
        request.user = self.user

        view = setup_view(
            views.FetchLeaderboardCommitsView(), request, self.leaderboard.id
        )
        response = view.get(request, self.leaderboard.id)
        # print(response.status_code)
        assert response.status_code == 302

    def test_leaderboard_details_view(self):
        """ Test GET method for leaderboard page with authenticated user """

        request = self.factory.get(
            reverse("leaderboard", kwargs={"id": self.leaderboard.id})
        )
        request.user = self.user

        view = setup_view(views.LeaderboardView(), request, self.leaderboard.id)
        response = view.get(request, self.leaderboard.id)

        assert response.status_code == 200

    def test_leaderboard_not_found(self):
        """ Test GET method to leaderboard page with invalid id and authenticated user """

        self.c.login(username="testuser", password="testpassword")

        url = reverse("leaderboard", kwargs={"id": 500})
        response = self.c.get(url)

        assert response.status_code == 404

    def test_leaderboard_not_found_unauthenticated_user(self):
        """ Test GET method to leaderboard detail with invalid id and unauthenticated user """

        url = reverse("leaderboard", kwargs={"id": 500})
        response = self.c.get(url)

        assert response.status_code == 302

    def test_close_leaderboard_if_ended(self):
        """ Test GET method to Close ended leaderboard with valid id and authenticated user """

        self.c.login(username="testuser", password="testpassword")

        url = reverse("close_leaderboard_if_ended", kwargs={"id": self.leaderboard.id})
        response = self.c.get(url)

        assert response.status_code == 302

    def test_manage_leaderboard_participants(self):
        """ Test GET and POST method to Manage leaderboard Participants view with valid id and authenticated user """

        self.c.login(username="testuser", password="testpassword")

        url = reverse(
            "manage_leaderboard_participants", kwargs={"id": self.leaderboard.id}
        )

        response = self.c.get(url)
        assert response.status_code == 200

        response = self.c.post(url)
        assert response.status_code == 400

        response = self.c.post(url, {"username": "fred"})
        assert response.status_code == 302

    def test_delete_leaderboard_participants(self):
        """ Test GET method to Delete leaderboard Participants view with valid id and authenticated user """

        self.c.login(username="testuser", password="testpassword")

        url = reverse(
            "delete_leaderboard_participants",
            kwargs={"id": self.leaderboard.id, "userid": self.user.id},
        )

        response = self.c.get(url)
        assert response.status_code == 302
