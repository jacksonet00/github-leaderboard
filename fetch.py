import requests

'''
Parameters:
  @username - the user, whose commits to be fetched
  @repo - name of repo whose commits are to be counter
  @owner - owner of the repo

Return:
  A list containing commits of user @username in the repo
  @repo, whose owner is @owner. Each commit will be a dict
  having following properites:
  {sha, message, date, verified}
'''
def fetch(username, repo, owner):
  response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/commits')

  # if status is not 200, i.e. response is not valid
  if response.status_code != 200:
    return None

  data = response.json()
  
  # filtering the commits of user 'username'
  filtered = filter(lambda x: x['commit']['author']['name'] == username, data)

  # defining returning data of each commit
  def map_commit(commit):
    return {
      'sha': commit['sha'],
      'message': commit['commit']['message'],
      'date': commit['commit']['author']['date'],
      'verified': commit['commit']['verification']['verified']
    }

  # mapping each commit to the previously defined object
  processed = map(map_commit, filtered)

  return list(processed)

# A simple test
# print(fetch('leeg8', 'github-leaderboard', 'jacksonet00'))