import os
import subprocess
import sys
import io

def is_git_repo():
    return subprocess.call(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0

def fetch_changes():
    subprocess.run(["git", "fetch"], check=True)

def get_status():
    result = subprocess.run(["git", "status", "--color=always"], capture_output=True, text=True)
    return result.stdout

def stage_changes():
    return input("Do you want to stage all changes? (y/n): ").lower() == 'y'

def commit_changes():
    commit_message = input("Enter commit message: ")
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

def push_changes():
    try:
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError:
        print("Push failed. There might be conflicts with the remote branch.")
        if input("Do you want to pull changes from remote? (y/n): ").lower() == 'y':
            try:
                subprocess.run(["git", "pull", "--rebase"], check=True)
                print("Pull successful. Trying to push again...")
                subprocess.run(["git", "push"], check=True)
            except subprocess.CalledProcessError:
                print("Conflicts detected. Please resolve conflicts manually, then commit and push.")
                sys.exit(1)

def main():
    if not is_git_repo():
        print("The current directory is not a Git repository.")
        return

    fetch_changes()
    
    status_output = get_status()
    print(status_output)

    if "Your branch is up to date" not in status_output or "nothing to commit" not in status_output:
        if stage_changes():
            subprocess.run(["git", "add", "-A"], check=True)
            commit_changes()
            push_changes()
            print("Changes have been staged, committed, and pushed.")
        else:
            print("No changes were staged or pushed.")
    else:
        print("No changes to commit or push.")

if __name__ == "__main__":
    main()