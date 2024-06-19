import os
import subprocess

def run_git_command(command):
    """Run a git command and check for errors."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Standard Output: {e.stdout}")
        print(f"Standard Error: {e.stderr}")
        raise

def main():
    # Get the directory, username, email, and commit message from the user
    directory = input("Enter the directory to initialize the git repository in: ").strip()
    username = input("Enter your GitHub username: ").strip()
    useremail = input("Enter your GitHub email: ").strip()
    commit_message = input("Enter the commit message: ").strip()

    # Ask for the preferred git host
    git_host = input("Enter the git host (github/gitlab/baltig): ").strip().lower()

    if git_host not in ['github', 'gitlab', 'baltig']:
        print("Invalid git host. Please enter 'github', 'gitlab', or 'baltig'.")
        return
    
    # Change to the specified directory
    os.chdir(directory)
    
    # Initialize the git repository
    run_git_command('git init')

    # Configure user details
    run_git_command(f'git config user.name "{username}"')
    run_git_command(f'git config user.email "{useremail}"')

    # Get the local repository name (assumed to be the name of the current directory)
    repo_name = os.path.basename(os.getcwd())
    
    # Prompt user to create a remote repository with the name "repo_name" on the chosen git host, otherwise git remote add origin will fail
    input(f"Have you created a repository with name {repo_name} on your remote {git_host} account? Press Enter to continue...")
    ask_prompt = input(f"Ok, let's proceed...")

    # Set the remote origin based on the chosen git host
    if git_host == 'github':
        run_git_command(f'git remote add origin https://github.com/{username}/{repo_name}.git')
    elif git_host == 'gitlab':
        run_git_command(f'git remote add origin https://gitlab.com/{username}/{repo_name}.git')
    elif git_host == 'baltig':
        run_git_command(f'git remote add origin https://baltig/{username}/{repo_name}.git')
    
    # Ask user for .gitignore options
    # Remember to NOT add the .git folder here (it would break git)
    default_gitignore = [
        '*.log',
        '*.tmp',
        '*.bak',
        '*.swp',
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '.DS_Store',
        'node_modules/',
        'venv/'
    ]

    custom_ignore = input("Do you want to provide a custom .gitignore list? (yes/no): ").strip().lower()

    if custom_ignore == 'yes':
        ignore_list = input("Enter the files/folders to ignore, separated by commas: ").strip().split(',')
    else:
        ignore_list = default_gitignore

    with open('.gitignore', 'w') as gitignore_file:
        for item in ignore_list:
            gitignore_file.write(item.strip() + '\n')
    
    # Change branch to main
    run_git_command('git branch -M main')
    
    # Add all files in the current folder to the staging area
    run_git_command('git add *')

    # Perform a complete stage
    run_git_command('git add -A')

    # Commit the changes
    run_git_command(f'git commit -m "{commit_message}"')

    # Push to the remote repository
    run_git_command('git push -u origin main')

if __name__ == "__main__":
    main()
