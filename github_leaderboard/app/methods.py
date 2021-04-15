import requests
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from . import models

User = get_user_model()

"""
given a link header from github, find the link for the next url which they use for pagination
"""


def find_next(link):
    for link in link.split(","):
        a, b = link.split(";")
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


# TODO: add more an error that says if the github link does not exist
def refresh_leaderboard_commits(id):
    leaderboard = get_object_or_404(models.Leaderboard, id=id)
    if leaderboard.closed:
        return False

    url_str = leaderboard.repo_url.replace("https://github.com/", "").strip("/")

    user = leaderboard.owner.github_username
    token = leaderboard.access_token
    commits_url = "https://api.github.com/repos/" + url_str + "/commits"
    # commits_url = 'https://api.github.com/repos/jacksonet00/github-leaderboard/commits'

    commits = models.Commit.objects.all().order_by("-timestamp")
    if commits.exists():
        latest_commit = commits[0]
        # print(latest_commit)
    else:
        latest_commit = None

    commits = []
    next_url = commits_url
    # Github responses are paginated this removes the pages
    while True:
        response = requests.get(next_url, auth=(user, token))
        page = response.json()

        commits.extend(page)  # Add objects from page to our list

        # Github returns commits ordered by latest timestamp.
        # So, if page contains latest commit present on our system, then stop process
        # because, later commits must be already present in our system
        if len(page) == 0:
            break
        if response.headers.get("link") is None:
            break
        next_url = find_next(response.headers["link"])
        if next_url is None:
            break
        if latest_commit:
            if latest_commit.nodeid in set(commit["node_id"] for commit in page):
                break

    updated = 0
    if response.status_code == 200:
        for commit in commits:
            if models.Commit.objects.filter(nodeid=commit["node_id"]).exists():
                continue  # skip if commit object already exists
            # u = User.objects.filter(github_username=x['commit']['author']['name'])
            user = User.objects.filter(
                github_username=commit["author"]["login"]
            )  # corrected to get github username instead of full name
            if user.exists():
                user = user.first()
            else:
                user = None  # save commit even if user(author) doesnot exist in our databse.
                # OR
                # continue # don't save commits made by users which doesn't exists on our system

            models.Commit.objects.create(
                leaderboard=leaderboard,
                user=user,
                nodeid=commit["node_id"],
                message=commit["commit"]["message"],
                url=commit["url"],
                html_url=commit["html_url"],
                timestamp=commit["commit"]["author"]["date"],
            )
            updated += 1
        return {"total": len(commits), "new": updated}

    return False
