import os
from dotenv import load_dotenv
from github_api import get_repo_star_count, get_count_repositories_with_at_least_stars, get_total_repositories_count


def main():
    home_directory = os.path.expanduser('~')
    dotenv_path = os.path.join(home_directory, '.env')
    load_dotenv(dotenv_path=dotenv_path)

    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if GITHUB_TOKEN is None:
        print("GitHub token not found. Please check your .env configuration.")
        return

    owner = 'colinmcnamara'
    repo = 'austin_langchain'

    # Get the current star count of the repository
    star_count = get_repo_star_count(GITHUB_TOKEN, owner, repo)
    if star_count is None:
        print("Unable to fetch star count.")
        return

    # Get the count of repositories with at least as many stars
    count_at_least_stars = get_count_repositories_with_at_least_stars(GITHUB_TOKEN, star_count)
    if count_at_least_stars is None:
        print("Unable to fetch the count of repositories with at least the same number of stars.")
        return

    # Get the total number of repositories
    total_repos = get_total_repositories_count(GITHUB_TOKEN)
    if total_repos is None:
        print("Unable to fetch the total number of repositories.")
        return

    # Print the results
    print(f"The repository {owner}/{repo} has {star_count} stars.")
    print(f"Total number of repositories with at least {star_count} stars: {count_at_least_stars}")
    if total_repos > 0:
        percentage = (count_at_least_stars / total_repos) * 100
        print(f"Percentage of repositories with at least {star_count} stars: {percentage:.2f}%")
    else:
        print("No repositories found to compare.")

if __name__ == '__main__':
    main()
