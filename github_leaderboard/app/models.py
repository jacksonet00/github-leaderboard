import datetime as dt

from django.db import models

from github_leaderboard.users.models import User


# Create your models here.
class Result(models.Model):
    def default_score():
        return 0

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=default_score)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.score} points"


class Leaderboard(models.Model):
    def default_start_datetime():
        return dt.datetime.now()

    def default_end_datetime():
        return dt.datetime.now() + dt.timedelta(days=7)

    name = models.CharField(max_length=255)
    start = models.DateTimeField(default=default_start_datetime)
    end = models.DateTimeField(default=default_end_datetime)
    repo_url = models.URLField(blank=True, null=True)
    access_token = models.CharField(max_length=255, unique=True, blank=True, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    results = models.ForeignKey(Result, blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(User,blank=True, related_name="leaderboards_participated")

    def __str__(self):
        return self.name


class Commit(models.Model):
    leaderboard = models.ForeignKey('Leaderboard', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nodeid = models.CharField(max_length=100)
    message = models.TextField()
    url = models.URLField()
    html_url = models.URLField()
    timestamp = models.DateTimeField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.timestamp} - {self.message} commits"
