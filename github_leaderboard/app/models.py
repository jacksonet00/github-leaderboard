from django.db import models
from github_leaderboard.users.models import User
import datetime as dt


# Create your models here.

class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    github_key = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user}"


class Result(models.Model):
    def default_score():
        return 0

    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    score = models.IntegerField(default=default_score)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{user}: {score} points"


class Leaderboard(models.Model):
    def default_start_datetime():
        return dt.datetime.now()

    def default_end_datetime():
        return dt.datetime.now() + dt.timedelta(days=7)

    name = models.CharField(max_length=255)
    start = models.DateTimeField(default=default_start_datetime)
    end = models.DateTimeField(default=default_end_datetime)
    repo_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(ExtendedUser, blank=True, null=True, on_delete=models.CASCADE)
    results = models.ForeignKey(Result, blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Commit(models.Model):
    def default_commit_count():
        return 0

    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    commit_count = models.IntegerField(default=default_commit_count)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.commit_count} commits"
