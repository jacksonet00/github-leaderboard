from django.shortcuts import get_object_or_404
import requests
import json

from . import models
from django.contrib.auth import get_user_model
User = get_user_model()

def refresh_leaderboard_commits(id):
    leaderboard = get_object_or_404(models.Leaderboard, id=id)
    url_str = leaderboard.repo_url.replace('https://github.com/','').strip("/")
    
    user = leaderboard.owner.github_username
    token = leaderboard.access_token
    commits_url = 'https://api.github.com/repos/'+ url_str + '/commits'
    # commits_url = 'https://api.github.com/repos/jacksonet00/github-leaderboard/commits'
    
    r=requests.get(commits_url,auth=(user, token))

    l = r.json()
    print(l)
    updated = 0
    if(r.status_code == 200):
        print(l[0])
        for x in l:
            if(models.CommitRecord.objects.filter(nodeid=x['node_id']).exists() ):
                continue # skip if commit object already exists
            u = User.objects.filter(github_username=x['commit']['author']['name'])
            if u.exists():
                u = u.first()
            else:
                u = None  # save commit even if user(author) doesnot exist in our databse.
                # OR
                # continue # don't save commits made by users which doesn't exists on our system

            models.CommitRecord.objects.create(
                leaderboard=leaderboard,
                user=u,
                nodeid=x['node_id'],
                message=x['commit']['message'],
                url=x['url'],
                html_url=x['html_url'],
                timestamp=x['commit']['author']['date'],
                )
            updated += 1
        return {"total":len(l), 'new': updated}
    
    return False
    