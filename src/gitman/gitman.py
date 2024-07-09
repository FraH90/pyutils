import os
import sys
import subprocess
import requests
import argparse

class GitManager:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

    def run_command(self, command, cwd=None):
        try:
            result = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True, check=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(f"Standard Output: {e.stdout}")
            print(f"Standard Error: {e.stderr}")
            return None

    def is_git_repo(self, path='.'):
        return self.run_command("git rev-parse --is-inside-work-tree", cwd=path) is not None

    def init_repo(self):
        directory = input("Enter the directory to initialize the git repository in: ").strip()
        username = input("Enter your GitHub username: ").strip()
        useremail = input("Enter your GitHub email: ").strip()
        commit_message = input("Enter the commit message: ").strip()
        git_host = input("Enter the git host (github/gitlab/baltig): ").strip().lower()

        if git_host not in ['github', 'gitlab', 'baltig']:
            print("Invalid git host. Please enter 'github', 'gitlab', or 'baltig'.")
            return

        os.chdir(directory)
        self.run_command('git init')
        self.run_command(f'git config user.name "{username}"')
        self.run_command(f'git config user.email "{useremail}"')

        repo_name = os.path.basename(os.getcwd())
        input(f"Have you created a repository with name {repo_name} on your remote {git_host} account? Press Enter to continue...")

        remote_url = f"https://{git_host}.com/{username}/{repo_name}.git"
        if git_host == 'baltig':
            remote_url = f"https://baltig.infn.it/{username}/{repo_name}.git"
        self.run_command(f'git remote add origin {remote_url}')

        self.create_gitignore()
        self.run_command('git branch -M main')
        self.run_command('git add -A')
        self.run_command(f'git commit -m "{commit_message}"')
        self.run_command('git push -u origin main')

    def create_gitignore(self):
        default_gitignore = [
            '*.log', '*.tmp', '*.bak', '*.swp', '__pycache__/', '*.pyc', '*.pyo',
            '.DS_Store', 'node_modules/', 'venv/'
        ]
        custom_ignore = input("Do you want to provide a custom .gitignore list? (yes/no): ").strip().lower()
        if custom_ignore == 'yes':
            ignore_list = input("Enter the files/folders to ignore, separated by commas: ").strip().split(',')
        else:
            ignore_list = default_gitignore
        
        with open('.gitignore', 'w') as gitignore_file:
            for item in ignore_list:
                gitignore_file.write(item.strip() + '\n')

    def clone_account_repos(self):
        username = input("Enter the GitHub username: ")
        ignore_archived = input("Do you want to ignore archived repositories? (yes/no): ").strip().lower() == 'yes'
        
        repositories = self.get_repositories(username)
        if not repositories:
            print("No repositories found or there was an error fetching them.")
            return

        ignore_list = self.read_ignore_list('repo_ignore.txt')
        
        repos_to_clone = [repo for repo in repositories if repo['name'] not in ignore_list and not (ignore_archived and repo['archived'])]

        if repos_to_clone:
            print("\nRepositories to be cloned:")
            for repo in repos_to_clone:
                print(f"- {repo['name']} ({repo['html_url']})")
            
            if input("\nDo you want to clone all listed repositories? (yes/no): ").strip().lower() == "yes":
                for repo in repos_to_clone:
                    self.run_command(f"git clone {repo['clone_url']}")

    def get_repositories(self, username):
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch repositories for user {username}: {response.status_code}")
            return []

    def read_ignore_list(self, filename):
        filepath = os.path.join(self.script_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        return []

    def push_all_repos(self):
        base_dir = input("Enter the path to the base directory: ").strip()
        if not os.path.isdir(base_dir):
            print("The provided path is not a valid directory.")
            return

        ignore_list = self.read_ignore_list('repo_ignore.txt')
        git_repos = self.find_git_repositories(base_dir)

        if not git_repos:
            print("No Git repositories found in the specified directory.")
            return

        for repo in git_repos:
            repo_name = os.path.basename(repo)
            if repo_name in ignore_list:
                print(f"Skipping repository {repo_name} as it is in the ignore list.")
                continue

            print(f"\nProcessing repository: {repo}")
            if input("Do you want to add, commit, and push changes to this repository? (yes/no): ").strip().lower() == 'yes':
                commit_message = input(f"Enter the commit message for {repo_name}: ").strip()
                self.run_command('git add .', cwd=repo)
                self.run_command(f'git commit -m "{commit_message}"', cwd=repo)
                self.run_command('git push origin main', cwd=repo)
            else:
                print(f"Skipping repository {repo_name} as per user request.")

    def find_git_repositories(self, base_dir):
        git_repos = []
        for root, dirs, files in os.walk(base_dir):
            if '.git' in dirs:
                git_repos.append(root)
                dirs[:] = []  # Don't descend into subdirectories
        return git_repos

    def stage_commit_push(self):
        if not self.is_git_repo():
            print("The current directory is not a Git repository.")
            return

        self.run_command("git fetch")
        status_output = self.run_command("git status")
        print("\n--- Git Status ---")
        print(status_output)
        print("------------------\n")

        if "nothing to commit, working tree clean" not in status_output:
            if input("\nDo you want to stage all changes? (y/n): ").lower() == 'y':
                self.run_command("git add -A")
                commit_message = input("\nEnter commit message: ")
                self.run_command(f'git commit -m "{commit_message}"')
                self.push_changes()
            else:
                print("No changes were staged or pushed.")
        else:
            print("No changes to commit or push.")

    def push_changes(self):
        print("\nPushing changes to remote...")
        push_result = self.run_command("git push")
        if push_result is None:
            if input("\nPush failed. Do you want to pull changes from remote? (y/n): ").lower() == 'y':
                pull_result = self.run_command("git pull --rebase")
                if pull_result is not None:
                    print("Pull successful. Trying to push again...")
                    self.run_command("git push")
                else:
                    print("\nConflicts detected. Please resolve conflicts manually, then commit and push.")
                    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Git Manager - A comprehensive Git management tool")
    parser.add_argument("--init", action="store_true", help="Initialize a new Git repository")
    parser.add_argument("--clonerepo", action="store_true", help="Clone all repositories from a GitHub account")
    parser.add_argument("--pushallrepo", action="store_true", help="Push changes for all repositories in a directory")
    parser.add_argument("--scp", action="store_true", help="Stage, commit, and push changes for the current repository")
    
    args = parser.parse_args()

    git_manager = GitManager()

    if len(sys.argv) == 1:
        # If no arguments are provided, run the interactive menu
        while True:
            print("\nGit Manager Menu:")
            print("1. Initialize a new Git repository")
            print("2. Clone all repositories from a GitHub account")
            print("3. Push changes for all repositories in a directory")
            print("4. Stage, commit, and push changes for the current repository")
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                git_manager.init_repo()
            elif choice == '2':
                git_manager.clone_account_repos()
            elif choice == '3':
                git_manager.push_all_repos()
            elif choice == '4':
                git_manager.stage_commit_push()
            elif choice == '5':
                print("Exiting Git Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        # Handle command-line arguments
        if args.init:
            git_manager.init_repo()
        elif args.clonerepo:
            git_manager.clone_account_repos()
        elif args.pushallrepo:
            git_manager.push_all_repos()
        elif args.scp:
            git_manager.stage_commit_push()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()