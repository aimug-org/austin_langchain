import requests

def get_repo_star_count(token, owner, repo):
    """Fetch the number of stars for a given repository."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['stargazers_count']
    else:
        print(f"Failed to fetch repository data: {response.status_code} {response.text}")
        return None

def get_count_repositories_with_at_least_stars(token, stars):
    """Fetch the count of repositories with at least the specified number of stars."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    query = f"stars:>={stars}"
    url = f"https://api.github.com/search/repositories?q={query}&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['total_count']
    else:
        print(f"Failed to fetch count for repositories with at least {stars} stars: {response.status_code} {response.text}")
        return None

def get_total_repositories_count(token):
    """Fetch the total number of repositories on GitHub."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # We use a generic search that all repositories will match.
    query = "size:>=0"
    url = f"https://api.github.com/search/repositories?q={query}&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['total_count']
    else:
        print(f"Failed to fetch total repository count: {response.status_code} {response.text}")
        return None

