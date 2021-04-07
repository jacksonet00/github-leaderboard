import datetime as dt

from django.db import models
from django.db.models import Count

from github_leaderboard.users.models import User
from datetime import datetime
from . import methods
from django.contrib.auth import get_user_model

User = get_user_model()
import pytz


# Create your models here.
class Result(models.Model):
    def default_score():
        return 0

    leaderboard = models.ForeignKey('Leaderboard', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='results')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=default_score)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.score} points"

    def save(self, *args, **kwargs):
        if (self.leaderboard):
            if (self.leaderboard.closed == True):
                raise ValueError("Updating results of closed leaderboard is not allowed")
        super().save(*args, **kwargs)


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
    # results = models.ForeignKey(Result, blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(User, blank=True, related_name="leaderboards_participated")
    closed = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Leaderboard, self).__init__(*args, **kwargs)
        self.initial_closed = self.closed  # remember initial value

    '''
    Comment this method if you want to edit the leaderboard during development
    '''

    # def save(self, *args, **kwargs):
    #     print(self.initial_closed) # value before save
    #     print(self.closed)  # value after save
    #     if(self.initial_closed == False):   # if leaderboard is not closed before current save
    #         super(Leaderboard, self).save(*args, **kwargs)
    #     else: # if leaderboard is already closed before current save
    #         raise ValueError("Updating closed leaderboard is not allowed")

    # update leaderboard commit data from repo
    def refresh(self):
        print("Refreshing Leaderboard " + str(self.name) + " Data")
        success = methods.refresh_leaderboard_commits(self.id)
        return success  # example success={'total': 12, 'new': 0} or success=False

    def get_ranked_user_commit_data(self):
        # users who have atleast one commit
        ranked_data = Commit.objects.filter(leaderboard=self, user__in=self.participants.all()).values(
            'user__github_username').annotate(total=Count('user')).order_by('-total')

        # users who dont have any commit
        users_without_commit = []  # list
        for user in self.participants.all():
            commit_count = user.commit_set.filter(leaderboard=self).count()
            if (commit_count == 0):
                # only add users who dont have any commit data in database
                users_without_commit.append(user)

        return ranked_data, users_without_commit
        # ranked_data, users_without_commit = (<QuerySet [{'user__github_username': 'leeg8', 'total': 5}, {'user__github_username': 'awhigham9', 'total': 3}, {'user__github_username': 'jacksonet00', 'total': 3}, {'user__github_username': 'f0lie', 'total': 1}]>, [<User: admin>])

    def close_if_ended(self):
        if (self.closed == False):
            today = pytz.UTC.localize(datetime.now())
            if (today > self.end):
                print('Closing leaderboard ' + str(self.name))
                self.refresh()  # fetch latest commit data from repo before closing
                ranked_data, users_without_commit = self.get_ranked_user_commit_data()
                for entry in ranked_data:
                    user = User.objects.get(github_username=entry['user__github_username'])
                    Result.objects.create(leaderboard=self, user=user, score=entry['total'])

                for user in users_without_commit:
                    Result.objects.create(leaderboard=self, user=user, score=0)

                self.closed = True
                self.save()
                print('leaderboard ' + str(self.name) + " closed successfully.")
        # else:
        #     raise ValueError("closing of already closed leaderboard is not allowed")

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

    def save(self, *args, **kwargs):
        if (self.leaderboard):
            if (self.leaderboard.closed == True):
                raise ValueError("Updating commits of closed leaderboard is not allowed")
        super().save(*args, **kwargs)
