import subprocess
import sys

def is_git_repo():
    return subprocess.call(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL) == 0

def fetch_changes():
    print("Fetching changes from remote...")
    result = subprocess.run(["git", "fetch"], capture_output=True, text=True)
    print(result.stdout)

def get_status():
    try:
        result = subprocess.check_output(["git", "status", "--color=always"], stderr=subprocess.STDOUT, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"An error occurred while getting git status: {e.output}"

def stage_changes():
    return input("\nDo you want to stage all changes? (y/n): ").lower() == 'y'

def commit_changes():
    commit_message = input("\nEnter commit message: ")
    result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
    print("\n--- Git Commit Output ---")
    print(result.stdout)
    print(result.stderr)
    print("-------------------------\n")

def push_changes():
    print("\nPushing changes to remote...")
    try:
        result = subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
        print("\n--- Git Push Output ---")
        print(result.stdout)
        print(result.stderr)
        print("-----------------------\n")
    except subprocess.CalledProcessError as e:
        print("\nPush failed. There might be conflicts with the remote branch.")
        print(e.stdout)
        print(e.stderr)
        if input("\nDo you want to pull changes from remote? (y/n): ").lower() == 'y':
            try:
                pull_result = subprocess.run(["git", "pull", "--rebase"], capture_output=True, text=True, check=True)
                print("\n--- Git Pull Output ---")
                print(pull_result.stdout)
                print(pull_result.stderr)
                print("-----------------------\n")
                print("Pull successful. Trying to push again...")
                push_result = subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
                print("\n--- Git Push Output ---")
                print(push_result.stdout)
                print(push_result.stderr)
                print("-----------------------\n")
            except subprocess.CalledProcessError as e:
                print("\nConflicts detected. Please resolve conflicts manually, then commit and push.")
                print(e.stdout)
                print(e.stderr)
                sys.exit(1)

def main():
    if not is_git_repo():
        print("The current directory is not a Git repository.")
        return

    fetch_changes()
    
    status_output = get_status()
    print("\n--- Git Status ---")
    print(status_output)
    print("------------------\n")

    if status_output and ("Your branch is up to date" not in status_output or "nothing to commit" not in status_output):
        if stage_changes():
            stage_result = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
            print("\n--- Git Add Output ---")
            print(stage_result.stdout)
            print(stage_result.stderr)
            print("-----------------------\n")
            commit_changes()
            push_changes()
            print("Changes have been staged, committed, and pushed.")
        else:
            print("No changes were staged or pushed.")
    else:
        print("No changes to commit or push.")

if __name__ == "__main__":
    main()