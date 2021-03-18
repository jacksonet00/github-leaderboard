import requests
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from . import models

User = get_user_model()

'''
given a link header from github, find the link for the next url which they use for pagination
'''


def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]


def is_obj_in_page(o, page):
    for obj in page:
        if (obj['node_id'] == o.nodeid):
            return True
    return False


def refresh_leaderboard_commits(id):
    leaderboard = get_object_or_404(models.Leaderboard, id=id)
    url_str = leaderboard.repo_url.replace('https://github.com/', '').strip("/")

    user = leaderboard.owner.github_username
    token = leaderboard.access_token
    commits_url = 'https://api.github.com/repos/' + url_str + '/commits'
    # commits_url = 'https://api.github.com/repos/jacksonet00/github-leaderboard/commits'

    commits = models.Commit.objects.all().order_by('-timestamp')
    if commits.exists():
        latest_commit = commits[0]
        # print(latest_commit)
    else:
        latest_commit = None

    l = []
    next_url = commits_url
    while True:
        r = requests.get(next_url, auth=(user, token))
        page = r.json()

        l.extend(page)  # Add objects from page to our list

        # Github returns commits ordered by latest timestamp.
        # So, if page contains latest commit present on our system, then stop process
        # because, later commits must be already present in our system
        if (latest_commit):
            if (is_obj_in_page(latest_commit, page)):
                break

        n = len(page)
        print(n)
        if n == 0:
            break
        link = r.headers.get('link')
        if link is None:
            break
        next_url = find_next(r.headers['link'])
        if next_url is None:
            break

    # print(l[:2])
    updated = 0
    if r.status_code == 200:
        # print(l[0])
        for x in l:
            if models.Commit.objects.filter(nodeid=x['node_id']).exists():
                continue  # skip if commit object already exists
            u = User.objects.filter(github_username=x['commit']['author']['name'])
            if u.exists():
                u = u.first()
            else:
                u = None  # save commit even if user(author) doesnot exist in our databse.
                # OR
                # continue # don't save commits made by users which doesn't exists on our system

            models.Commit.objects.create(
                leaderboard=leaderboard,
                user=u,
                nodeid=x['node_id'],
                message=x['commit']['message'],
                url=x['url'],
                html_url=x['html_url'],
                timestamp=x['commit']['author']['date'],
            )
            updated += 1
        return {"total": len(l), 'new': updated}

    return False
