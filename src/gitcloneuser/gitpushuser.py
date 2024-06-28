import os
import subprocess

def find_git_repositories(base_dir):
    git_repos = []
    for root, dirs, files in os.walk(base_dir):
        if '.git' in dirs:
            git_repos.append(root)
            dirs[:] = []  # Don't descend into subdirectories
    return git_repos

def add_untracked_files(repo_path):
    result = subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully added files in {repo_path}")
    else:
        print(f"Failed to add files in {repo_path}: {result.stderr}")

def commit_changes(repo_path, commit_message):
    result = subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully committed changes in {repo_path}")
    else:
        print(f"Failed to commit changes in {repo_path}: {result.stderr}")

def push_changes(repo_path):
    result = subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully pushed changes in {repo_path}")
    else:
        print(f"Failed to push changes in {repo_path}: {result.stderr}")

def read_ignore_list(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    return []

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    ignore_list = read_ignore_list(os.path.join(script_dir, 'repo_ignore.txt'))

    base_dir = input("Enter the path to the base directory: ").strip()
    if not os.path.isdir(base_dir):
        print("The provided path is not a valid directory.")
        return

    git_repos = find_git_repositories(base_dir)
    
    if not git_repos:
        print("No Git repositories found in the specified directory.")
        return

    for repo in git_repos:
        repo_name = os.path.basename(repo)
        if repo_name in ignore_list:
            print(f"Skipping repository {repo_name} as it is in the ignore list.")
            continue
        
        print(f"\nProcessing repository: {repo}")
        permission = input("Do you want to add, commit, and push changes to this repository? (yes/no): ").strip().lower()
        if permission == 'yes':
            commit_message = input(f"Enter the commit message for {repo_name}: ").strip()
            add_untracked_files(repo)
            commit_changes(repo, commit_message)
            push_changes(repo)
        else:
            print(f"Skipping repository {repo_name} as per user request.")

if __name__ == "__main__":
    main()
