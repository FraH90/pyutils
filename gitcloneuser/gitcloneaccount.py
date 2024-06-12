import requests
import subprocess
import os

def get_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch repositories for user {username}: {response.status_code}")
        return []

def clone_repository(repo_url):
    result = subprocess.run(["git", "clone", repo_url], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully cloned {repo_url}\n")
    else:
        print(f"Failed to clone {repo_url}: {result.stderr}\n")

def read_ignore_list(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return []

def main():
    username = input("Enter the GitHub username: ")
    repositories = get_repositories(username)
    
    if not repositories:
        print("No repositories found or there was an error fetching them.")
        return

    ignore_list = read_ignore_list('repo_ignore.txt')
    ignore_archived = input("Do you want to ignore archived repositories? (yes/no): ").strip().lower() == 'yes'

    print(f"\nFound {len(repositories)} repositories for user {username}:\n")
    
    repos_to_clone = []
    repos_ignored_archive = []
    repos_ignored_list = []

    for repo in repositories:
        if repo['name'] in ignore_list:
            repos_ignored_list.append(repo)
        elif ignore_archived and repo['archived']:
            repos_ignored_archive.append(repo)
        else:
            repos_to_clone.append(repo)

    if repos_to_clone:
        print("Repositories to be cloned:")
        for repo in repos_to_clone:
            print(f"- {repo['name']} ({repo['html_url']})")
        print()

    if repos_ignored_list:
        print("Repositories ignored due to repo_ignore.txt:")
        for repo in repos_ignored_list:
            print(f"- {repo['name']} ({repo['html_url']})")
        print()

    if repos_ignored_archive:
        print("Repositories ignored because they are archived:")
        for repo in repos_ignored_archive:
            print(f"- {repo['name']} ({repo['html_url']})")
        print()

    clone_all = input("Do you want to clone all listed repositories? (yes/no): ").strip().lower()
    if clone_all == "yes":
        for repo in repos_to_clone:
            clone_repository(repo['clone_url'])

if __name__ == "__main__":
    main()
