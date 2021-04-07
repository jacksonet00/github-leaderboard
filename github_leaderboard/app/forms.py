from django import forms

from github_leaderboard.app.models import Leaderboard


class CreateLeaderboardForm(forms.ModelForm):
    class Meta:
        model = Leaderboard
        fields = ("name", "repo_url", "end", "start")
